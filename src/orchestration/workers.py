"""Concrete AgentWorker implementations for multi-agent workflows.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import logging
from typing import Any

from .task import Task
from .executor import AgentWorker

try:
    from .creative_workers import creative_workers as _creative_workers
except ImportError:  # pragma: no cover

    def _creative_workers():
        return {}

logger = logging.getLogger("SaphiraWorkers")


class BaseSkillWorker:
    name: str = "base"
    capabilities: set[str] = set()
    skill: str = ""

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    def _envelope(self, task: Task, step: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "completed",
            "agent": self.name,
            "skill": self.skill,
            "step": step.get("name"),
            "capability": step.get("capability"),
            "task_id": task.id,
            "payload": payload,
        }


class ResearchWorker(BaseSkillWorker):
    name = "research_agent"
    capabilities = {"research", "web"}
    skill = "deepsearch"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {"summary": f"Research brief for: {task.objective}", "sources": [], "confidence": 0.7},
        )


class DeveloperWorker(BaseSkillWorker):
    name = "developer_agent"
    capabilities = {"development", "system"}
    skill = "saphira-build"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {"summary": f"Implementation plan for: {task.objective}", "files_touched": []},
        )


class QualityWorker(BaseSkillWorker):
    name = "qa_agent"
    capabilities = {"quality"}
    skill = "verification"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"passed": True, "checks": ["policy", "coherence"]})


class ContentWorker(BaseSkillWorker):
    name = "content_agent"
    capabilities = {"content"}
    skill = "content"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"summary": f"Draft for: {task.objective}", "format": "markdown"})


class CodeReviewerWorker(BaseSkillWorker):
    name = "code_reviewer_agent"
    capabilities = {"code_review", "development", "quality"}
    skill = "saphira-code-reviewer"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"review": {"severity": "info"}})


class SystemsArchitectWorker(BaseSkillWorker):
    name = "systems_architect_agent"
    capabilities = {"architecture", "system", "development"}
    skill = "saphira-systems-architect"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"architecture": {"pipeline": "fixed"}})


class DataAnalystWorker(BaseSkillWorker):
    name = "data_analyst_agent"
    capabilities = {"analytics", "research", "stem"}
    skill = "saphira-data-analyst"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"analysis": {"method": "descriptive"}})


class SecurityAuditorWorker(BaseSkillWorker):
    name = "security_auditor_agent"
    capabilities = {"security", "quality", "code_review"}
    skill = "saphira-security-auditor"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(task, step, {"audit": {"severity": "info"}})


class ReasoningWorker(BaseSkillWorker):
    name = "planner_agent"
    capabilities = {"reasoning"}
    skill = "think-mode"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task, step, {"synthesis": f"Reasoned summary for: {task.objective}", "mode": "think"}
        )


def default_workers() -> dict[str, AgentWorker]:
    """Factory of all built-in skill workers including creative co-creation."""
    workers: list[BaseSkillWorker] = [
        ResearchWorker(),
        DeveloperWorker(),
        QualityWorker(),
        ContentWorker(),
        CodeReviewerWorker(),
        SystemsArchitectWorker(),
        DataAnalystWorker(),
        SecurityAuditorWorker(),
        ReasoningWorker(),
    ]
    out = {w.name: w for w in workers}  # type: ignore[misc]
    out.update(_creative_workers())
    return out
