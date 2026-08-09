"""Durable work model used by Saphira's execution runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNED = "planned"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AutonomyDecision:
    level: str = "autonomous"
    requires_approval: bool = False
    reason: str | None = None


@dataclass
class Task:
    objective: str
    context: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    status: TaskStatus = TaskStatus.CREATED
    priority: str = "normal"
    plan: list[dict[str, Any]] = field(default_factory=list)
    assigned_agents: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    autonomy: AutonomyDecision = field(default_factory=AutonomyDecision)
    approval_status: str = "not_required"
    verification: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def add_step(self, name: str, capability: str, **metadata: Any) -> None:
        self.plan.append({"name": name, "capability": capability, **metadata})
