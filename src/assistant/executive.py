"""Saphira's single conversational executive interface.

Users interact with this class; workers, tools, routing and memory remain
implementation details behind it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.autonomy.policy import AutonomyPolicy
from src.memory.operational import OperationalMemory
from src.orchestration.executor import ExecutionResult, TaskExecutor
from src.orchestration.planner import TaskPlanner
from src.orchestration.registry import AgentRegistry
from src.orchestration.task import Task, TaskStatus


@dataclass
class SaphiraExecutive:
    planner: TaskPlanner = field(default_factory=TaskPlanner)
    registry: AgentRegistry = field(default_factory=AgentRegistry)
    autonomy: AutonomyPolicy = field(default_factory=AutonomyPolicy)
    executor: TaskExecutor = field(default_factory=TaskExecutor)
    memory: OperationalMemory = field(default_factory=OperationalMemory)
    active_tasks: dict[str, Task] = field(default_factory=dict)

    def accept(self, message: str, context: dict[str, Any] | None = None) -> Task:
        """Understand, plan, classify and route a conversational request."""
        merged = dict(context or {})
        merged.setdefault("recent_tasks", self.memory.recent_tasks())
        task = self.planner.create_task(message=message, context=merged)
        task.autonomy = self.autonomy.classify(task)
        self.registry.route(task)
        if task.autonomy.requires_approval:
            task.approval_status = "pending"
            task.set_status(TaskStatus.WAITING_APPROVAL)
        self.active_tasks[task.id] = task
        return task

    def approve(self, task_id: str) -> Task:
        task = self._get(task_id)
        task.approval_status = "approved"
        task.emit("approval_granted")
        return task

    def reject(self, task_id: str, reason: str = "Rejected by user") -> Task:
        task = self._get(task_id)
        task.approval_status = "rejected"
        task.errors.append(reason)
        task.set_status(TaskStatus.CANCELLED)
        return task

    async def execute(self, task_id: str) -> ExecutionResult:
        task = self._get(task_id)
        result = await self.executor.run(task)
        self.memory.record_task(task.id, task.objective, task.status.value, {
            "artifacts": result.artifacts,
            "errors": result.errors,
        })
        return result

    def respond(self, task: Task) -> str:
        """Return a concise user-facing response while workers remain hidden."""
        if task.status == TaskStatus.WAITING_APPROVAL:
            return f"I’ve prepared this: {task.objective}. I need your approval before I take the restricted action."
        if task.status == TaskStatus.COMPLETED:
            return f"Done. I completed: {task.objective}"
        if task.status == TaskStatus.FAILED:
            return f"I hit a problem while handling: {task.objective}. I’ve preserved the task state so we can recover from it."
        return f"Got it. I’m handling this now: {task.objective}"

    def _get(self, task_id: str) -> Task:
        try:
            return self.active_tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"Unknown Saphira task: {task_id}") from exc
