"""Provider isolation facade used by Saphira connector adapters."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    ok: bool
    value: Any = None
    error: str | None = None


async def invoke_provider(provider: str, operation: Callable[[], Awaitable[Any]], *,
                          timeout_seconds: float = 15.0) -> ProviderResult:
    """Convert an individual provider failure/timeout into a result, not a process crash."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    try:
        return ProviderResult(provider, True,
                              await asyncio.wait_for(operation(), timeout=timeout_seconds))
    except (Exception, asyncio.TimeoutError) as exc:
        return ProviderResult(provider, False, error=f"{type(exc).__name__}: {exc}")


async def invoke_providers(providers: list[tuple[str, Callable[[], Awaitable[Any]]]], *,
                           timeout_seconds: float = 15.0) -> list[ProviderResult]:
    async def one(item: tuple[str, Callable[[], Awaitable[Any]]]) -> ProviderResult:
        return await invoke_provider(item[0], item[1], timeout_seconds=timeout_seconds)
    return list(await asyncio.gather(*(one(item) for item in providers)))
