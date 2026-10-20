"""Enforced memory API — all platform paths should import from here.

Forces TenantMemoryGuard; raw TenantMemoryStore is not for agent use.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.platform.memory.hybrid import MemoryRecord, TenantMemoryStore, memory_store
from src.platform.memory.tenant_guard import (
    MissingTenantError,
    TenantIsolationError,
    TenantMemoryGuard,
    tenant_memory,
)

guard: TenantMemoryGuard = tenant_memory


def remember(
    *,
    tenant_id: str | None,
    user_id: str | None,
    content: str,
    kind: str = "episodic",
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
    execution_id: str | None = None,
) -> MemoryRecord:
    return guard.add(
        tenant_id=tenant_id,
        user_id=user_id,
        content=content,
        kind=kind,
        confidence=confidence,
        metadata=metadata,
        execution_id=execution_id,
    )


def recall(
    *,
    tenant_id: str | None,
    user_id: str | None,
    kind: Optional[str] = None,
) -> List[MemoryRecord]:
    return guard.list(tenant_id=tenant_id, user_id=user_id, kind=kind)


def forget(
    *,
    tenant_id: str | None,
    user_id: str | None,
    record_id: str,
) -> bool:
    return guard.delete(tenant_id=tenant_id, user_id=user_id, record_id=record_id)


__all__ = [
    "MemoryRecord",
    "MissingTenantError",
    "TenantIsolationError",
    "TenantMemoryGuard",
    "guard",
    "remember",
    "recall",
    "forget",
    "memory_store",
]
