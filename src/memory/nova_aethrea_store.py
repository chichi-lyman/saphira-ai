# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# NovaAethreaMemoryStore — elite hybrid memory (vector + graph + episodic)
# Absolute permanent recall with tenant isolation and policy gates.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger("NovaAethreaMemory")


class MemoryKind(str, Enum):
    IDENTITY = "identity"
    PREFERENCE = "preference"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    RELATIONSHIP = "relationship"
    TASK_OUTCOME = "task_outcome"
    SCENE = "scene"


@dataclass
class MemoryRecord:
    id: str
    tenant_id: str
    kind: MemoryKind
    content: Dict[str, Any]
    embedding: Optional[List[float]] = None
    graph_links: List[str] = field(default_factory=list)
    confidence: float = 1.0
    decay_half_life_days: float = 90.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    sensitivity: str = "internal"  # public | internal | confidential
    provenance: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            {"kind": self.kind.value, "content": self.content}, sort_keys=True
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:32]


class NovaAethreaMemoryStore:
    """
    Elite hybrid memory for Saphira / NovaAethrea.

    - Vector store for semantic recall
    - Graph edges for relationships and causal chains
    - Episodic timeline
    - Tenant isolation + sensitivity gates
    - Session consolidation into durable preferences
    - Hot path for identity + preferences
    """

    def __init__(
        self,
        vector_backend: Any = None,
        graph_backend: Any = None,
        kv_backend: Any = None,
    ):
        # Backends are optional; fall back to in-memory for development
        self.vector = vector_backend
        self.graph = graph_backend
        self.kv = kv_backend or _InMemoryKV()
        self._records: Dict[str, MemoryRecord] = {}

    async def write(
        self, record: MemoryRecord, policy_ok: bool = True
    ) -> str:
        if not policy_ok:
            raise PermissionError("Memory write blocked by policy")
        record.hash = record.compute_hash()
        key = f"{record.tenant_id}:{record.hash}"
        existing = await self.kv.get(key)
        if existing:
            return existing

        self._records[record.id] = record
        await self.kv.set(key, record.id)

        if self.vector is not None:
            try:
                await self.vector.upsert(record)
            except Exception as e:
                logger.warning("vector upsert failed: %s", e)

        if self.graph is not None:
            try:
                await self.graph.add_node(record)
                for link in record.graph_links:
                    await self.graph.add_edge(record.id, link)
            except Exception as e:
                logger.warning("graph write failed: %s", e)

        if record.kind in (MemoryKind.IDENTITY, MemoryKind.PREFERENCE):
            await self.kv.set(
                f"hot:{record.tenant_id}:{record.kind.value}", record.content
            )

        return record.id

    async def recall(
        self,
        tenant_id: str,
        query: str,
        kinds: Optional[List[MemoryKind]] = None,
        top_k: int = 12,
        max_bytes: int = 12_000,
    ) -> List[MemoryRecord]:
        # Simple in-memory hybrid for bootstrap; replace with real backends later
        candidates = [
            r
            for r in self._records.values()
            if r.tenant_id == tenant_id
            and (kinds is None or r.kind in kinds)
        ]

        # Naive relevance: keyword overlap + recency
        scored = []
        q_lower = query.lower()
        for r in candidates:
            text = json.dumps(r.content).lower()
            score = sum(1 for tok in q_lower.split() if tok in text)
            score += r.confidence
            scored.append((score, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [r for _, r in scored[:top_k]]
        return self._budget(top, max_bytes)

    async def consolidate_session(
        self, tenant_id: str, session_transcript: List[Dict[str, Any]]
    ) -> None:
        """Session → durable preferences + episodic summary."""
        if not session_transcript:
            return
        summary = {
            "turns": len(session_transcript),
            "last_user": session_transcript[-1].get("text", "")[:300]
            if session_transcript
            else "",
        }
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            kind=MemoryKind.EPISODIC,
            content=summary,
            provenance={"source": "session_consolidation"},
        )
        await self.write(record)

    def _budget(
        self, records: List[MemoryRecord], max_bytes: int
    ) -> List[MemoryRecord]:
        out: List[MemoryRecord] = []
        size = 0
        for r in records:
            chunk = len(json.dumps(r.content))
            if size + chunk > max_bytes:
                break
            out.append(r)
            size += chunk
        return out


class _InMemoryKV:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        return self._store.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._store[key] = value
