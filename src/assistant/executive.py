"""Canonical conversational entrypoint for Saphira.

Saphira owns the user relationship. Background agents are implementation
workers and are never exposed as separate assistants by this layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.orchestration.planner import TaskPlanner
from src.orchestration.registry import AgentRegistry
from src.orchestration.task import Task
from src.autonomy.policy import AutonomyPolicy


@dataclass
class SaphiraExecutive:
    planner: TaskPlanner
    registry: AgentRegistry
    autonomy: AutonomyPolicy

    def accept(self, message: str, context: dict[str, Any] | None = None) -> Task:
        """Convert a conversational request into an executable task graph."""
        context = context or {}
        task = self.planner.create_task(message=message, context=context)
        task.autonomy = self.autonomy.classify(task)
        task.assigned_agents = self.registry.route(task)
        return task

    def respond(self, task: Task) -> str:
        """Produce the conversational acknowledgement for a task."""
        if task.autonomy.requires_approval:
            return f"I understand. I’ve prepared the work, but I need your approval before I execute the restricted step: {task.objective}"
        return f"Got it. I’m handling this now: {task.objective}"
