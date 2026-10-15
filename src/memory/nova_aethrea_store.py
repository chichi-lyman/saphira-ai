# © 2026 Chelsea Megan Woods
# Lean NovaAethreaMemoryStore — in-memory hybrid, O(1) hot path, bounded recall.

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import time
import uuid

class Kind(str, Enum):
    ID = "id"
    PREF = "pref"
    EPI = "epi"
    SEM = "sem"
    OUT = "out"

@dataclass
class Rec:
    id: str
    tenant: str
    kind: Kind
    content: Dict[str, Any]
    conf: float = 1.0
    ts: float = field(default_factory=time.time)
    h: str = ""

    def hash(self) -> str:
        b = json.dumps({"k": self.kind.value, "c": self.content}, sort_keys=True).encode()
        return hashlib.sha256(b).hexdigest()[:24]

class NovaAethreaMemoryStore:
    __slots__ = ("_rec", "_hot", "_idx", "writes", "reads")

    def __init__(self):
        self._rec: Dict[str, Rec] = {}
        self._hot: Dict[str, Any] = {}          # tenant:kind -> content
        self._idx: Dict[str, str] = {}          # tenant:hash -> id
        self.writes = 0
        self.reads = 0

    async def write(self, rec: Rec, policy_ok: bool = True) -> str:
        if not policy_ok:
            raise PermissionError("blocked")
        rec.h = rec.hash()
        key = f"{rec.tenant}:{rec.h}"
        if key in self._idx:
            return self._idx[key]
        self._rec[rec.id] = rec
        self._idx[key] = rec.id
        if rec.kind in (Kind.ID, Kind.PREF):
            self._hot[f"{rec.tenant}:{rec.kind.value}"] = rec.content
        self.writes += 1
        return rec.id

    async def write_outcome(self, tenant: str, agent: str, result: Dict[str, Any]) -> None:
        r = Rec(
            id=str(uuid.uuid4()),
            tenant=tenant,
            kind=Kind.OUT,
            content={"agent": agent, "status": result.get("status"), "summary": str(result.get("message", ""))[:200]},
        )
        await self.write(r)

    async def recall(self, tenant: str, query: str, top_k: int = 8, max_bytes: int = 8000) -> List[Any]:
        self.reads += 1
        q = query.lower().split()
        scored = []
        for r in self._rec.values():
            if r.tenant != tenant:
                continue
            text = json.dumps(r.content).lower()
            score = sum(1 for t in q if t in text) + r.conf
            scored.append((score, r))
        scored.sort(key=lambda x: (-x[0], -x[1].ts))
        out, size = [], 0
        for _, r in scored[:top_k]:
            chunk = len(json.dumps(r.content))
            if size + chunk > max_bytes:
                break
            out.append(r.content)
            size += chunk
        return out

    def metrics(self) -> Dict[str, int]:
        return {"writes": self.writes, "reads": self.reads, "records": len(self._rec)}
