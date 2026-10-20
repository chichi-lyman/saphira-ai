"""Worker timeout policy and enforced async watchdog for Saphira.

The hard deadline cancels the awaited task. Python cannot safely kill arbitrary
synchronous code running in a thread; workers should use async, cancellable IO or
process isolation for untrusted/blocking workloads.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class WorkerTimeoutPolicy:
    soft_seconds: float = 8.0
    hard_seconds: float = 15.0
    max_specialist_hops: int = 10
    on_timeout: str = "abort_safe_default"

    def __post_init__(self) -> None:
        if self.soft_seconds <= 0:
            raise ValueError("soft_seconds must be greater than zero")
        if self.hard_seconds <= 0:
            raise ValueError("hard_seconds must be greater than zero")
        if self.hard_seconds < self.soft_seconds:
            raise ValueError("hard_seconds must be greater than or equal to soft_seconds")
        if self.max_specialist_hops < 1:
            raise ValueError("max_specialist_hops must be at least one")


DEFAULT_WORKER_TIMEOUTS = WorkerTimeoutPolicy()


class WorkerExecutionTimeout(TimeoutError):
    """Raised when an awaited specialist exceeds its hard deadline."""


def should_abort_loop(hop_count: int, policy: WorkerTimeoutPolicy | None = None) -> bool:
    """Return True when the next specialist hop would exceed the configured budget."""
    p = policy or DEFAULT_WORKER_TIMEOUTS
    return hop_count >= p.max_specialist_hops


async def run_with_watchdog(
    operation: Callable[[], Awaitable[T]] | Awaitable[T],
    *,
    policy: WorkerTimeoutPolicy | None = None,
    on_soft_timeout: Callable[[float], Any] | None = None,
) -> T:
    """Run an awaitable with a soft warning and an enforced hard deadline.

    The soft hook is observational; the operation is allowed to continue until the
    hard deadline. At the hard deadline the asyncio task is cancelled and a
    WorkerExecutionTimeout is raised. Cancellation is cooperative.
    """
    p = policy or DEFAULT_WORKER_TIMEOUTS
    awaitable = operation() if callable(operation) else operation
    if not inspect.isawaitable(awaitable):
        raise TypeError("run_with_watchdog requires an awaitable operation")

    task = asyncio.ensure_future(awaitable)
    started = time.monotonic()
    done, _ = await asyncio.wait({task}, timeout=p.soft_seconds)
    if done:
        return task.result()

    if on_soft_timeout is not None:
        on_soft_timeout(time.monotonic() - started)

    remaining = max(0.0, p.hard_seconds - (time.monotonic() - started))
    try:
        return await asyncio.wait_for(task, timeout=remaining)
    except asyncio.TimeoutError as exc:
        if not task.done():
            task.cancel()
        raise WorkerExecutionTimeout(
            f"Specialist exceeded hard deadline of {p.hard_seconds:.3f}s"
        ) from exc
