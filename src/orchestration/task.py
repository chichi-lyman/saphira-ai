"""Durable task and execution-state models for Saphira."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNED = "planned"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AutonomyDecision:
    level: str = "autonomous"
    requires_approval: bool = False
    reason: str | None = None
    risk: str = "low"


@dataclass
class TaskEvent:
    type: str
    task_id: str
    timestamp: str = field(default_factory=utc_now)
    payload: dict[str, Any] = field(default_factory=dict)


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
    events: list[TaskEvent] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    completed_at: str | None = None

    def add_step(self, name: str, capability: str, **metadata: Any) -> None:
        self.plan.append({"id": f"step_{uuid4().hex[:8]}", "name": name, "capability": capability, "status": "pending", **metadata})

    def emit(self, event_type: str, **payload: Any) -> TaskEvent:
        event = TaskEvent(event_type, self.id, payload=payload)
        self.events.append(event)
        return event

    def set_status(self, status: TaskStatus) -> None:
        self.status = status
        if status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            self.completed_at = utc_now()
        self.emit("status_changed", status=status.value)
