"""Dual-tier memory ledger — fast RAM cache + durable persistence.

Links temporary session context with persistent storage (JSON today,
PostgreSQL/pgvector when DATABASE_URL + embeddings are configured).

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Optional

from src.memory.persistent_store import PersistentMemoryStore, persistent_memory


@dataclass
class MemoryEntry:
    key: str
    value: Any
    tier: str  # "ram" | "durable"
    created_at: float = field(default_factory=time.time)
    tags: tuple[str, ...] = ()


class DualMemoryLedger:
    """RAM LRU + durable store for continuous context across sessions."""

    def __init__(
        self,
        *,
        ram_capacity: int = 256,
        store: Optional[PersistentMemoryStore] = None,
    ) -> None:
        self._ram: OrderedDict[str, MemoryEntry] = OrderedDict()
        self._capacity = max(16, ram_capacity)
        self._lock = threading.Lock()
        self._store = store or persistent_memory
        self._pg_url = os.getenv("DATABASE_URL") or os.getenv("SAPHIRA_DATABASE_URL")

    # --- RAM tier ---

    def put_ram(self, key: str, value: Any, *, tags: tuple[str, ...] = ()) -> MemoryEntry:
        entry = MemoryEntry(key=key, value=value, tier="ram", tags=tags)
        with self._lock:
            if key in self._ram:
                self._ram.pop(key)
            self._ram[key] = entry
            while len(self._ram) > self._capacity:
                self._ram.popitem(last=False)
        return entry

    def get_ram(self, key: str) -> Optional[MemoryEntry]:
        with self._lock:
            entry = self._ram.get(key)
            if entry is None:
                return None
            self._ram.move_to_end(key)
            return entry

    # --- Durable tier ---

    def put_durable(self, key: str, value: Any) -> None:
        self._store.set_fact(key, value)
        self.put_ram(key, value, tags=("durable",))

    def get_durable(self, key: str) -> Any:
        cached = self.get_ram(key)
        if cached is not None:
            return cached.value
        value = self._store.get_fact(key)
        if value is not None:
            self.put_ram(key, value, tags=("durable",))
        return value

    def append_turn(self, role: str, content: str, **meta: Any) -> str:
        turn_id = str(uuid.uuid4())
        entry = {
            "id": turn_id,
            "role": role,
            "content": content,
            "ts": time.time(),
            **meta,
        }
        self._store.append_history(entry)
        self.put_ram(f"turn:{turn_id}", entry, tags=("history",))
        return turn_id

    def recent_context(self, limit: int = 12) -> list[dict[str, Any]]:
        return self._store.get_history(limit)

    def context_pack(self, **kwargs: Any) -> dict[str, Any]:
        pack = self._store.build_context_pack(**kwargs)
        pack["ram_keys"] = list(self._ram.keys())[-32:]
        pack["pgvector_configured"] = bool(self._pg_url)
        pack["tier"] = "dual"
        return pack

    def memory_check(self) -> dict[str, Any]:
        with self._lock:
            ram_size = len(self._ram)
        history = self._store.get_history(5)
        return {
            "status": "ok",
            "ram_entries": ram_size,
            "ram_capacity": self._capacity,
            "recent_history": len(history),
            "pgvector_configured": bool(self._pg_url),
            "durable_backend": "postgres+pgvector" if self._pg_url else "file_json",
        }


# Process-wide dual ledger
dual_memory = DualMemoryLedger()
