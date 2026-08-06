# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Short-term session memory + long-term persistent memory facade.

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional

try:
    from src.memory.persistent_store import PersistentStore  # type: ignore
except Exception:  # pragma: no cover
    PersistentStore = None  # type: ignore


@dataclass
class Turn:
    role: str
    content: str
    ts: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)


class SessionMemory:
    """In-process short-term memory per session_id."""

    def __init__(self, max_turns: int = 40):
        self._max_turns = max_turns
        self._turns: Dict[str, Deque[Turn]] = defaultdict(lambda: deque(maxlen=max_turns))
        self._scratch: Dict[str, Dict[str, Any]] = defaultdict(dict)

    def append(self, session_id: str, role: str, content: str, **meta: Any) -> None:
        self._turns[session_id].append(Turn(role=role, content=content, meta=meta))

    def history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        turns = list(self._turns.get(session_id, []))
        if last_n is not None:
            turns = turns[-last_n:]
        return [{"role": t.role, "content": t.content, "ts": t.ts, **t.meta} for t in turns]

    def set_scratch(self, session_id: str, key: str, value: Any) -> None:
        self._scratch[session_id][key] = value

    def get_scratch(self, session_id: str, key: str, default: Any = None) -> Any:
        return self._scratch[session_id].get(key, default)

    def clear(self, session_id: str) -> None:
        self._turns.pop(session_id, None)
        self._scratch.pop(session_id, None)


class PersistentMemory:
    """
    Long-term memory: preferences, projects, facts.
    Uses PersistentStore when available; otherwise in-process fallback.
    """

    def __init__(self):
        self._local: Dict[str, Any] = {
            "preferences": {},
            "projects": {},
            "facts": [],
            "home_topology": {},
        }
        self._store = None
        if PersistentStore is not None:
            try:
                self._store = PersistentStore()
            except Exception:
                self._store = None

    def remember_preference(self, key: str, value: Any) -> None:
        self._local["preferences"][key] = value
        self._maybe_persist("preferences", self._local["preferences"])

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._local["preferences"].get(key, default)

    def remember_project(self, name: str, data: Dict[str, Any]) -> None:
        self._local["projects"][name] = {**data, "updated_at": time.time()}
        self._maybe_persist("projects", self._local["projects"])

    def add_fact(self, fact: str, tags: Optional[List[str]] = None) -> str:
        item = {
            "id": str(uuid.uuid4())[:8],
            "fact": fact,
            "tags": tags or [],
            "ts": time.time(),
        }
        self._local["facts"].append(item)
        # keep bounded
        self._local["facts"] = self._local["facts"][-500:]
        return item["id"]

    def search_facts(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        q = query.lower()
        hits = [f for f in self._local["facts"] if q in f["fact"].lower()]
        return hits[-limit:]

    def set_home_topology(self, topology: Dict[str, Any]) -> None:
        self._local["home_topology"] = topology
        self._maybe_persist("home_topology", topology)

    def context_block(self, query: Optional[str] = None) -> str:
        """Plain-text block for system prompt injection."""
        prefs = self._local["preferences"]
        projects = list(self._local["projects"].keys())[:5]
        facts = self.search_facts(query or "", limit=5) if query else self._local["facts"][-5:]
        lines = ["[LONG-TERM MEMORY]"]
        if prefs:
            lines.append("Preferences: " + ", ".join(f"{k}={v}" for k, v in list(prefs.items())[:12]))
        if projects:
            lines.append("Projects: " + ", ".join(projects))
        for f in facts:
            lines.append(f"- {f.get('fact', f)}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def snapshot(self) -> Dict[str, Any]:
        return {
            "preferences_count": len(self._local["preferences"]),
            "projects_count": len(self._local["projects"]),
            "facts_count": len(self._local["facts"]),
            "backend": "persistent_store" if self._store else "local",
        }

    def _maybe_persist(self, key: str, value: Any) -> None:
        if self._store is None:
            return
        try:
            if hasattr(self._store, "set"):
                self._store.set(key, value)
            elif hasattr(self._store, "save"):
                self._store.save(key, value)
        except Exception:
            pass


# Process singletons
session_memory = SessionMemory()
persistent_memory = PersistentMemory()
