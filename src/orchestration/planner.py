"""Deterministic first-pass task planning with an LLM-ready contract."""
from __future__ import annotations

import re
from typing import Any

from .task import Task, TaskStatus


CAPABILITY_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("research", ("research", "find", "compare", "investigate", "look up", "analyze"), "research"),
    ("development", ("build", "code", "fix", "github", "deploy", "implement", "debug"), "development"),
    ("content", ("content", "script", "post", "youtube", "social", "write", "seo"), "content"),
    ("commerce", ("shopify", "store", "product", "commerce", "sell", "order"), "commerce"),
    ("communications", ("email", "message", "contact", "outreach", "reply", "follow up"), "communications"),
    ("scheduling", ("calendar", "schedule", "meeting", "appointment", "remind"), "scheduling"),
    ("operations", ("organize", "file", "document", "workflow", "automate", "cleanup"), "operations"),
)


class TaskPlanner:
    """Build a small inspectable graph; an LLM planner can replace this later."""

    def create_task(self, message: str, context: dict[str, Any] | None = None) -> Task:
        objective = re.sub(r"\s+", " ", message.strip())
        if not objective:
            raise ValueError("Saphira needs a non-empty objective.")
        task = Task(objective=objective, context=context or {})
        text = objective.lower()
        task.add_step("understand objective", "reasoning")

        matched = False
        for name, terms, capability in CAPABILITY_RULES:
            if any(term in text for term in terms):
                task.add_step(name, capability)
                matched = True

        if not matched:
            task.add_step("reason about objective", "reasoning")
        task.add_step("verify result", "quality")
        task.set_status(TaskStatus.PLANNED)
        task.emit("task_planned", step_count=len(task.plan))
        return task
