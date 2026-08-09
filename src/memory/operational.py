"""Small operational memory abstraction used by the executive runtime.

The store is intentionally dependency-free. It can later be backed by the
repository's persistent memory/vector layer without changing Saphira's API.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OperationalMemory:
    facts: dict[str, Any] = field(default_factory=dict)
    task_summaries: list[dict[str, Any]] = field(default_factory=list)

    def remember(self, key: str, value: Any) -> None:
        self.facts[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self.facts.get(key, default)

    def record_task(self, task_id: str, objective: str, status: str, result: dict[str, Any] | None = None) -> None:
        self.task_summaries.append({
            "task_id": task_id,
            "objective": objective,
            "status": status,
            "result": result or {},
        })
        self.task_summaries = self.task_summaries[-100:]

    def recent_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.task_summaries[-limit:]
