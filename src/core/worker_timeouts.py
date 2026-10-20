"""Worker / sub-task timeout policy for executive pipeline.

Prevents hung specialists from locking Celery/Redis under load.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerTimeoutPolicy:
    soft_seconds: float = 8.0
    hard_seconds: float = 15.0
    max_specialist_hops: int = 10
    on_timeout: str = "abort_safe_default"


DEFAULT_WORKER_TIMEOUTS = WorkerTimeoutPolicy()


def should_abort_loop(hop_count: int, policy: WorkerTimeoutPolicy | None = None) -> bool:
    p = policy or DEFAULT_WORKER_TIMEOUTS
    return hop_count >= p.max_specialist_hops
