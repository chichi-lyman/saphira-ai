# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Persistent memory storage for NovaAethrea
# File-backed JSON store (can be swapped for SQLite / pgvector later)

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger("SaphiraMemory")

DEFAULT_PATH = os.getenv("SAPHIRA_MEMORY_PATH", "data/nova_aethrea_memory.json")


class PersistentMemoryStore:
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                self._data = {}
        else:
            self._data = {"facts": {}, "preferences": {}, "scenes": {}, "history": []}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def set_fact(self, key: str, value: Any):
        self._data.setdefault("facts", {})[key] = value
        self._save()

    def get_fact(self, key: str) -> Optional[Any]:
        return self._data.get("facts", {}).get(key)

    def set_preference(self, key: str, value: Any):
        self._data.setdefault("preferences", {})[key] = value
        self._save()

    def get_preference(self, key: str) -> Optional[Any]:
        return self._data.get("preferences", {}).get(key)

    def append_history(self, entry: Dict[str, Any]):
        history = self._data.setdefault("history", [])
        history.append(entry)
        # keep last 200 entries
        self._data["history"] = history[-200:]
        self._save()

    def get_history(self, limit: int = 20) -> list:
        return self._data.get("history", [])[-limit:]

    def save_scene(self, name: str, steps: list):
        self._data.setdefault("scenes", {})[name] = steps
        self._save()

    def get_scene(self, name: str) -> Optional[list]:
        return self._data.get("scenes", {}).get(name)

    def all_data(self) -> Dict[str, Any]:
        return self._data


# Singleton used by NovaAethrea
persistent_memory = PersistentMemoryStore()
