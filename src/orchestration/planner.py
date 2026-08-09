"""Intent-to-task planning for Saphira.

The planner deliberately produces a small, inspectable task graph. A future
LLM planner can replace the heuristic decomposition without changing the
Task contract or the executive interface.
"""

from __future__ import annotations

from typing import Any

from .task import Task, TaskStatus


class TaskPlanner:
    def create_task(self, message: str, context: dict[str, Any] | None = None) -> Task:
        objective = message.strip()
        task = Task(objective=objective, context=context or {})

        text = objective.lower()
        task.add_step("understand objective", "reasoning")

        if any(word in text for word in ("research", "find", "compare", "investigate")):
            task.add_step("research", "research")
        if any(word in text for word in ("build", "code", "fix", "github", "deploy")):
            task.add_step("implement", "development")
        if any(word in text for word in ("content", "script", "post", "youtube", "social")):
            task.add_step("create content", "content")
        if any(word in text for word in ("shopify", "store", "product", "commerce", "sell")):
            task.add_step("operate commerce", "commerce")
        if any(word in text for word in ("email", "message", "contact", "outreach")):
            task.add_step("handle communications", "communications")

        task.add_step("verify result", "quality")
        task.status = TaskStatus.PLANNED
        return task
