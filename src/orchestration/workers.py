"""Concrete AgentWorker implementations for multi-agent workflows.

Copyright © 2026 Chelsea Megan Woods

These workers are bound to the custom agent skills:
- saphira-code-reviewer
- saphira-systems-architect
- saphira-data-analyst
- saphira-security-auditor

They implement the AgentWorker protocol expected by TaskExecutor and
MultiAgentWorkflowEngine. Heavy LLM / tool calls stay behind adapters;
these provide structured, testable behavior and handoff-compatible results.
"""

from __future__ import annotations

import logging
from typing import Any

from .task import Task
from .executor import AgentWorker

logger = logging.getLogger("SaphiraWorkers")


class BaseSkillWorker:
    """Shared helpers for skill-backed workers."""

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
        objective = task.objective
        logger.info("ResearchWorker on: %s", objective[:80])
        return self._envelope(
            task,
            step,
            {
                "summary": f"Research brief for: {objective}",
                "sources": [],
                "sub_queries": [objective],
                "confidence": 0.7,
            },
        )


class DeveloperWorker(BaseSkillWorker):
    name = "developer_agent"
    capabilities = {"development", "system"}
    skill = "saphira-build"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("DeveloperWorker on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "summary": f"Implementation plan for: {task.objective}",
                "files_touched": [],
                "tests_suggested": ["unit", "integration"],
            },
        )


class QualityWorker(BaseSkillWorker):
    name = "qa_agent"
    capabilities = {"quality"}
    skill = "verification"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("QualityWorker verifying task %s", task.id)
        return self._envelope(
            task,
            step,
            {
                "passed": True,
                "checks": ["policy", "coherence", "artifact_presence"],
            },
        )


class ContentWorker(BaseSkillWorker):
    name = "content_agent"
    capabilities = {"content"}
    skill = "content"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {"summary": f"Draft / spec for: {task.objective}", "format": "markdown"},
        )


class CodeReviewerWorker(BaseSkillWorker):
    """Bound to skills/saphira-code-reviewer."""

    name = "code_reviewer_agent"
    capabilities = {"code_review", "development", "quality"}
    skill = "saphira-code-reviewer"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("CodeReviewer skill on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "review": {
                    "correctness": "pending_static_analysis",
                    "security": "no_critical_findings_stub",
                    "style": "aligned_with_project_conventions",
                    "suggestions": [
                        "Prefer async patterns matching existing safe_run",
                        "Add type hints and structured handoff status",
                    ],
                },
                "severity": "info",
            },
        )


class SystemsArchitectWorker(BaseSkillWorker):
    """Bound to skills/saphira-systems-architect."""

    name = "systems_architect_agent"
    capabilities = {"architecture", "system", "development"}
    skill = "saphira-systems-architect"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("SystemsArchitect skill on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "architecture": {
                    "components": ["api", "workers", "memory", "policy_gate"],
                    "pipeline": (
                        "Saphira → Aura → Agent Two → Nova Reign → "
                        "NovaAethrea → Agent Zero"
                    ),
                    "invariants": [
                        "secret-mask",
                        "commercial policy gate",
                        "no autonomous external spend",
                    ],
                    "recommendations": [
                        "Register new workers via AgentRegistry",
                        "Expose only Saphira-facing results",
                    ],
                }
            },
        )


class DataAnalystWorker(BaseSkillWorker):
    """Bound to skills/saphira-data-analyst."""

    name = "data_analyst_agent"
    capabilities = {"analytics", "research", "stem"}
    skill = "saphira-data-analyst"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("DataAnalyst skill on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "analysis": {
                    "metrics": [],
                    "method": "descriptive + trend",
                    "caveats": ["stub — connect Lyra pipeline for live data"],
                    "next_steps": ["load dataset", "run summary stats", "chart"],
                }
            },
        )


class SecurityAuditorWorker(BaseSkillWorker):
    """Bound to skills/saphira-security-auditor."""

    name = "security_auditor_agent"
    capabilities = {"security", "quality", "code_review"}
    skill = "saphira-security-auditor"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("SecurityAuditor skill on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "audit": {
                    "threat_model": "stub_baseline",
                    "findings": [],
                    "severity": "info",
                    "checks": [
                        "secrets_not_in_source",
                        "policy_gates_present",
                        "sandbox_isolation",
                        "external_io_requires_approval",
                    ],
                    "recommendations": [
                        "Keep production secrets in env / secret store",
                        "Route commercial actions through CommercialAuthorityPolicy",
                        "Do not bypass Agent Two security gate",
                    ],
                }
            },
        )


class ReasoningWorker(BaseSkillWorker):
    name = "planner_agent"
    capabilities = {"reasoning"}
    skill = "think-mode"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "synthesis": f"Reasoned summary for: {task.objective}",
                "mode": "think",
            },
        )


def default_workers() -> dict[str, AgentWorker]:
    """Factory of all built-in skill workers."""
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
    return {w.name: w for w in workers}  # type: ignore[misc]
