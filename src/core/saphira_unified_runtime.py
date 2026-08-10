"""Canonical contracts for the unified Saphira executive runtime.

This module is intentionally provider-neutral. Existing agents, tools, memory
providers, and device adapters can implement these contracts without forcing a
second orchestration stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class AutonomyLevel(str, Enum):
    OBSERVE = "observe"
    RECOMMEND = "recommend"
    APPROVE = "approve"
    EXECUTE = "execute"
    VERIFY = "verify"


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    domain: str
    autonomy: AutonomyLevel = AutonomyLevel.RECOMMEND
    side_effect: bool = False
    requires_approval: bool = False


@dataclass
class SaphiraRequest:
    user_id: str
    message: str
    tenant_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    id: str
    objective: str
    capability: str
    arguments: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    autonomy: AutonomyLevel = AutonomyLevel.RECOMMEND
    requires_approval: bool = False
    status: str = "pending"


@dataclass
class TaskResult:
    task_id: str
    success: bool
    output: Any = None
    error: str | None = None
    verified: bool = False
    audit: dict[str, Any] = field(default_factory=dict)


class CapabilityWorker(Protocol):
    async def execute(self, task: Task) -> TaskResult: ...


class MemoryStore(Protocol):
    async def recall(self, query: str, *, user_id: str, tenant_id: str | None = None) -> list[dict[str, Any]]: ...

    async def remember(
        self,
        record: dict[str, Any],
        *,
        user_id: str,
        tenant_id: str | None = None,
    ) -> None: ...


class CapabilityRegistry(Protocol):
    def resolve(self, capability: str) -> CapabilityWorker: ...

    def describe(self) -> list[Capability]: ...


class VerificationEngine(Protocol):
    async def verify(self, task: Task, result: TaskResult) -> TaskResult: ...


class ApprovalPolicy(Protocol):
    def requires_approval(self, task: Task, *, tenant_id: str | None = None) -> bool: ...


class ExecutiveRuntime(Protocol):
    async def handle(self, request: SaphiraRequest) -> str: ...


DEFAULT_CAPABILITIES: tuple[Capability, ...] = (
    Capability("reasoning", "General reasoning and decision support", "intelligence"),
    Capability("research", "Research, grounding, and synthesis", "research"),
    Capability("development", "Software engineering and repository workflows", "engineering"),
    Capability("sales", "Lead qualification, outreach, and pipeline workflows", "revenue", AutonomyLevel.APPROVE, True),
    Capability("growth", "Growth analysis and optimization", "revenue"),
    Capability("communications", "Messaging and communications workflows", "communications", AutonomyLevel.APPROVE, True),
    Capability("commerce", "Commerce, catalog, customer, and order workflows", "commerce", AutonomyLevel.APPROVE, True),
    Capability("creator", "Content planning and production workflows", "creative"),
    Capability("business_intelligence", "Business analytics and decision intelligence", "intelligence"),
    Capability("automation", "Workflow automation and scheduling", "automation", AutonomyLevel.APPROVE, True),
    Capability("device", "Permissioned device and environment operations", "device", AutonomyLevel.APPROVE, True),
    Capability("quality_assurance", "Verification, testing, and completion checks", "quality"),
)


def build_task_graph(objective: str, capabilities: list[str]) -> list[Task]:
    """Create a minimal capability task graph for an executive planner.

    A production planner can replace this helper with model-driven planning;
    the returned Task contract remains stable for workers and verification.
    """
    tasks: list[Task] = []
    previous: str | None = None
    for index, capability in enumerate(capabilities, start=1):
        task_id = f"task-{index}"
        tasks.append(
            Task(
                id=task_id,
                objective=objective,
                capability=capability,
                dependencies=[previous] if previous else [],
            )
        )
        previous = task_id
    return tasks
