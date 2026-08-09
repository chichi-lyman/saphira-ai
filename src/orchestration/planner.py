"""Deterministic first-pass task planning with an LLM-ready contract."""
from __future__ import annotations

import re
from typing import Any

from .task import Task, TaskStatus


CAPABILITY_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("research", ("research", "find", "compare", "investigate", "look up", "analyze", "fact check"), "research"),
    ("development", ("build", "code", "fix", "github", "deploy", "implement", "debug", "refactor", "test code"), "development"),
    ("content", ("content", "script", "post", "youtube", "social", "write", "seo", "caption"), "content"),
    ("commerce", ("shopify", "store", "product", "commerce", "sell", "order", "catalog"), "commerce"),
    ("communications", ("email", "message", "contact", "outreach", "reply", "follow up", "send"), "communications"),
    ("scheduling", ("calendar", "schedule", "meeting", "appointment", "remind", "deadline"), "scheduling"),
    ("operations", ("organize", "file", "document", "workflow", "automate", "cleanup", "operate"), "operations"),
    ("voice", ("voice", "speak", "listen", "audio", "transcribe", "read aloud"), "voice"),
    ("vision", ("image", "photo", "screenshot", "screen", "ocr", "camera", "look at"), "vision"),
    ("stem", ("calculate", "equation", "math", "physics", "engineering", "formula"), "stem"),
    ("cad", ("cad", "3d model", "openscad", "build123d", "3d print", "parametric"), "cad"),
    ("system", ("computer", "cpu", "gpu", "ram", "thermal", "application", "app", "terminal", "device"), "system"),
    ("iot", ("smart home", "home assistant", "matter", "lights", "thermostat", "sensor", "iot"), "iot"),
    ("web", ("web", "website", "online", "weather", "navigation", "current information", "search online"), "web"),
    ("memory", ("remember", "forget", "memory", "what did we decide", "my preference"), "memory"),
    ("proactive", ("monitor", "watch for", "when this happens", "every day", "every week", "automatically remind"), "proactive"),
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
