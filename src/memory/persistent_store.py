# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Persistent memory storage for NovaAethrea
# File-backed JSON store (can be swapped for SQLite / pgvector later)
# Extended with ContextPack builder and connector health for multi-agent handoffs.

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("SaphiraMemory")

DEFAULT_PATH = os.getenv("SAPHIRA_MEMORY_PATH", "data/nova_aethrea_memory.json")


class PersistentMemoryStore:
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.error("Failed to load memory: %s", e)
                self._data = {}
        if not self._data:
            self._data = {
                "facts": {},
                "preferences": {},
                "scenes": {},
                "history": [],
                "connector_health": {},
            }
        self._data.setdefault("facts", {})
        self._data.setdefault("preferences", {})
        self._data.setdefault("scenes", {})
        self._data.setdefault("history", [])
        self._data.setdefault("connector_health", {})

    def _save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Failed to save memory: %s", e)

    def set_fact(self, key: str, value: Any) -> None:
        self._data.setdefault("facts", {})[key] = value
        self._save()

    def get_fact(self, key: str) -> Optional[Any]:
        return self._data.get("facts", {}).get(key)

    def set_preference(self, key: str, value: Any) -> None:
        self._data.setdefault("preferences", {})[key] = value
        self._save()

    def get_preference(self, key: str) -> Optional[Any]:
        return self._data.get("preferences", {}).get(key)

    def append_history(self, entry: Dict[str, Any]) -> None:
        history = self._data.setdefault("history", [])
        history.append(entry)
        self._data["history"] = history[-200:]
        self._save()

    def get_history(self, limit: int = 20) -> list:
        return self._data.get("history", [])[-limit:]

    def save_scene(self, name: str, steps: list) -> None:
        self._data.setdefault("scenes", {})[name] = steps
        self._save()

    def get_scene(self, name: str) -> Optional[list]:
        return self._data.get("scenes", {}).get(name)

    def all_data(self) -> Dict[str, Any]:
        return self._data

    # --- Multi-agent extensions ---

    def update_connector_health(
        self,
        connector: str,
        *,
        status: str = "ok",
        retries: int = 0,
        last_error: Optional[str] = None,
    ) -> None:
        health = self._data.setdefault("connector_health", {})
        health[connector] = {
            "status": status,
            "retries": retries,
            "last_error": last_error,
            "last_success_ms": int(datetime.now(timezone.utc).timestamp() * 1000)
            if status == "ok"
            else health.get(connector, {}).get("last_success_ms"),
        }
        self._save()

    def get_connector_health(self) -> Dict[str, Any]:
        return dict(self._data.get("connector_health", {}))

    def build_context_pack(
        self,
        *,
        task_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        policy_grant: str = "ALLOW",
        history_limit: int = 10,
    ) -> Dict[str, Any]:
        """Assemble a ContextPack for NovaReign → NovaAethrea → Agent Zero handoffs."""
        return {
            "trace_id": trace_id or str(uuid.uuid4()),
            "task_id": task_id or str(uuid.uuid4()),
            "facts": dict(self._data.get("facts", {})),
            "preferences": dict(self._data.get("preferences", {})),
            "scenes": dict(self._data.get("scenes", {})),
            "history_slice": self.get_history(history_limit),
            "connector_health": self.get_connector_health(),
            "policy_grant": policy_grant,
            "built_at": datetime.now(timezone.utc).isoformat(),
        }


# Singleton used by NovaAethrea
persistent_memory = PersistentMemoryStore()
