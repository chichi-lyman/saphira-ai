"""Hybrid memory: episodic buffer, semantic facts, tenant isolation."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryRecord:
    id: str
    tenant_id: str
    user_id: str
    kind: str
    content: str
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantMemoryStore:
    def __init__(self) -> None:
        self._records: List[MemoryRecord] = []

    def add(self, tenant_id: str, user_id: str, content: str, kind: str = "episodic", confidence: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> MemoryRecord:
        rec = MemoryRecord(id=str(uuid.uuid4()), tenant_id=tenant_id, user_id=user_id, kind=kind, content=content, confidence=confidence, metadata=metadata or {})
        self._records.append(rec)
        return rec

    def list_for_user(self, tenant_id: str, user_id: str, kind: Optional[str] = None) -> List[MemoryRecord]:
        out = [r for r in self._records if r.tenant_id == tenant_id and r.user_id == user_id]
        if kind:
            out = [r for r in out if r.kind == kind]
        return out

    def distill_semantic(self, tenant_id: str, user_id: str, min_confidence: float = 0.7) -> List[MemoryRecord]:
        promoted: List[MemoryRecord] = []
        for r in self.list_for_user(tenant_id, user_id, kind="episodic"):
            if r.confidence >= min_confidence and len(r.content) > 20:
                semantic = self.add(tenant_id, user_id, content=r.content, kind="semantic", confidence=r.confidence, metadata={"source_episodic_id": r.id})
                promoted.append(semantic)
        return promoted

    def isolation_key(self, tenant_id: str, user_id: str) -> str:
        raw = f"{tenant_id}:{user_id}".encode()
        return hashlib.sha256(raw).hexdigest()[:16]


memory_store = TenantMemoryStore()
