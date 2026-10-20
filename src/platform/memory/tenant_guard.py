"""Tenant-enforced hybrid memory for Saphira / Nova Umbrella.

Extends TenantMemoryStore with hard isolation guarantees:
  - Every read/write requires tenant_id and user_id
  - Cross-tenant access raises TenantIsolationError (never returns other tenants' data)
  - Optional execution_id linkage for contract audit
  - Delete / retention controls scoped to tenant+user only

Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.platform.memory.hybrid import MemoryRecord, TenantMemoryStore, memory_store


class TenantIsolationError(PermissionError):
    """Raised when a memory operation violates tenant or user isolation."""


class MissingTenantError(ValueError):
    """Raised when tenant_id or user_id is missing."""


def _require_ids(tenant_id: str | None, user_id: str | None) -> tuple[str, str]:
    if not tenant_id or not str(tenant_id).strip():
        raise MissingTenantError("tenant_id is required for all memory operations")
    if not user_id or not str(user_id).strip():
        raise MissingTenantError("user_id is required for all memory operations")
    return str(tenant_id).strip(), str(user_id).strip()


@dataclass
class TenantMemoryGuard:
    """Facade over TenantMemoryStore that enforces isolation on every call."""

    store: TenantMemoryStore
    allow_empty_tenant: bool = False

    def add(
        self,
        *,
        tenant_id: str | None,
        user_id: str | None,
        content: str,
        kind: str = "episodic",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        execution_id: str | None = None,
    ) -> MemoryRecord:
        tid, uid = _require_ids(tenant_id, user_id)
        meta = dict(metadata or {})
        if execution_id:
            meta["execution_id"] = execution_id
        meta["isolation_key"] = self.store.isolation_key(tid, uid)
        return self.store.add(tid, uid, content=content, kind=kind, confidence=confidence, metadata=meta)

    def list(
        self,
        *,
        tenant_id: str | None,
        user_id: str | None,
        kind: Optional[str] = None,
    ) -> List[MemoryRecord]:
        tid, uid = _require_ids(tenant_id, user_id)
        rows = self.store.list_for_user(tid, uid, kind=kind)
        for r in rows:
            if r.tenant_id != tid or r.user_id != uid:
                raise TenantIsolationError(
                    f"Isolation breach: record {r.id} tenant/user mismatch"
                )
        return rows

    def get(
        self,
        *,
        tenant_id: str | None,
        user_id: str | None,
        record_id: str,
    ) -> MemoryRecord | None:
        tid, uid = _require_ids(tenant_id, user_id)
        for r in self.store.list_for_user(tid, uid):
            if r.id == record_id:
                if r.tenant_id != tid or r.user_id != uid:
                    raise TenantIsolationError(f"Isolation breach on get {record_id}")
                return r
        return None

    def delete(
        self,
        *,
        tenant_id: str | None,
        user_id: str | None,
        record_id: str,
    ) -> bool:
        tid, uid = _require_ids(tenant_id, user_id)
        before = len(self.store._records)
        self.store._records = [
            r
            for r in self.store._records
            if not (r.id == record_id and r.tenant_id == tid and r.user_id == uid)
        ]
        for r in self.store._records:
            if r.id == record_id:
                raise TenantIsolationError(
                    f"Refused to delete record {record_id}: belongs to another tenant/user"
                )
        return len(self.store._records) < before

    def distill_semantic(
        self,
        *,
        tenant_id: str | None,
        user_id: str | None,
        min_confidence: float = 0.7,
    ) -> List[MemoryRecord]:
        tid, uid = _require_ids(tenant_id, user_id)
        return self.store.distill_semantic(tid, uid, min_confidence=min_confidence)

    def assert_no_leak(
        self,
        *,
        tenant_id: str,
        user_id: str,
        other_tenant_id: str,
        other_user_id: str,
    ) -> None:
        a = {r.id for r in self.list(tenant_id=tenant_id, user_id=user_id)}
        b = {r.id for r in self.list(tenant_id=other_tenant_id, user_id=other_user_id)}
        if a & b:
            raise TenantIsolationError(f"Cross-tenant leak detected: {a & b}")


tenant_memory = TenantMemoryGuard(store=memory_store)
