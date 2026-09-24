# Copyright © 2026 Chelsea Megan Woods
"""Unified parent class for all Saphira specialist agents.

Provides the conversation loop, background-task hooks, memory logging
interface, anomaly classification, and human-in-the-loop checkpoint that
every agent under the fixed executive pipeline inherits.

Pipeline (invariant):
  Saphira (intent) → Aura (perception) → Agent Two (security)
  → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

from packages.saphira_core.personas import persona_for
from packages.saphira_core.registry import AGENTS, policy_for

logger = logging.getLogger("saphira.core.base_agent")


class AgentStatus(str, Enum):
    """Canonical status values returned by every specialist."""

    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"
    TIMEOUT = "TIMEOUT"


class AnomalyTier(str, Enum):
    """Risk tiers used for logging vs graceful rollback decisions."""

    INFO = "INFO"          # simple log only
    WARNING = "WARNING"    # log + optional soft recovery
    CRITICAL = "CRITICAL"  # immediate graceful rollback / HITL escalation


@dataclass
class AgentResult:
    """Structured envelope returned by process / safe_run."""

    agent: str
    status: AgentStatus
    output: Any = None
    next_agents: List[str] = field(default_factory=list)
    anomaly_tier: Optional[AnomalyTier] = None
    recovered_from_failure: bool = False
    requires_human_review: bool = False
    task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "status": self.status.value,
            "output": self.output,
            "next_agents": self.next_agents,
            "anomaly_tier": self.anomaly_tier.value if self.anomaly_tier else None,
            "recovered_from_failure": self.recovered_from_failure,
            "requires_human_review": self.requires_human_review,
            "task_id": self.task_id,
            "metadata": self.metadata,
        }


class MemoryStore(Protocol):
    """Minimal interface for NovaAethrea-style persistent memory."""

    async def log_interaction(
        self,
        agent: str,
        utterance: str,
        result: Dict[str, Any],
        tenant_id: str = "DEFAULT",
    ) -> None: ...

    async def recall(
        self,
        query: str,
        limit: int = 5,
        tenant_id: str = "DEFAULT",
    ) -> List[Dict[str, Any]]: ...


class HumanInTheLoopGate(Protocol):
    """Gate that must approve high-impact external actions before execution."""

    async def request_confirmation(
        self,
        agent: str,
        action_summary: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 120.0,
    ) -> bool: ...


# Default no-op implementations so agents remain testable without full infra.
class NullMemoryStore:
    async def log_interaction(
        self,
        agent: str,
        utterance: str,
        result: Dict[str, Any],
        tenant_id: str = "DEFAULT",
    ) -> None:
        logger.debug("NullMemoryStore: skip log for %s", agent)

    async def recall(
        self,
        query: str,
        limit: int = 5,
        tenant_id: str = "DEFAULT",
    ) -> List[Dict[str, Any]]:
        return []


class AutoApproveHITL:
    """Development / test gate that always approves. Production must inject a real gate."""

    async def request_confirmation(
        self,
        agent: str,
        action_summary: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 120.0,
    ) -> bool:
        logger.warning(
            "AutoApproveHITL used for agent=%s action=%s — replace in production",
            agent,
            action_summary[:80],
        )
        return True


class BaseAgent(ABC):
    """Parent class for the twelve specialist agents and any future adapters.

    Subclasses must implement `handle`. All other lifecycle concerns
    (persona, policy, safe execution, anomaly classification, memory,
    HITL) are provided here.
    """

    name: str = "base"
    description: str = "Base specialist agent"

    def __init__(
        self,
        memory: Optional[MemoryStore] = None,
        hitl_gate: Optional[HumanInTheLoopGate] = None,
        *,
        tenant_id: str = "DEFAULT",
    ) -> None:
        self.memory: MemoryStore = memory or NullMemoryStore()
        self.hitl_gate: HumanInTheLoopGate = hitl_gate or AutoApproveHITL()
        self.tenant_id = tenant_id
        self._background_tasks: Dict[str, asyncio.Task] = {}
        meta = AGENTS.get(self.name)
        self.default_policy = meta.default_policy if meta else policy_for(self.name)
        self.persona = persona_for(self.name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process(
        self,
        utterance: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Primary conversation-loop entry point used by the orchestrator."""
        context = context or {}
        task_id = context.get("task_id") or f"task_{uuid.uuid4().hex[:10]}"
        logger.info(
            "Agent %s processing task_id=%s utterance_len=%d",
            self.name,
            task_id,
            len(utterance or ""),
        )
        try:
            result = await self.safe_run(utterance, context, task_id=task_id)
            await self._log_memory(utterance, result)
            return result
        except Exception as exc:  # noqa: BLE001 — intentional top-level recovery
            return await self._classify_and_recover(exc, task_id=task_id)

    async def safe_run(
        self,
        utterance: str,
        context: Dict[str, Any],
        *,
        task_id: str,
    ) -> AgentResult:
        """Execute handle() under policy + optional HITL for high-impact actions."""
        if self.default_policy == "REQUIRE_APPROVAL":
            approved = await self.hitl_gate.request_confirmation(
                agent=self.name,
                action_summary=f"Policy-gated action for: {utterance[:120]}",
                payload={"utterance": utterance, "context": context},
            )
            if not approved:
                return AgentResult(
                    agent=self.name,
                    status=AgentStatus.REQUIRES_APPROVAL,
                    output={"reason": "human_review_denied_or_timeout"},
                    requires_human_review=True,
                    task_id=task_id,
                )

        raw = await self.handle(utterance, context)
        return self._normalize_result(raw, task_id=task_id)

    @abstractmethod
    async def handle(
        self,
        utterance: str,
        context: Dict[str, Any],
    ) -> Any:
        """Specialist-specific logic. Must be implemented by every subclass."""

    # ------------------------------------------------------------------
    # Background task helpers
    # ------------------------------------------------------------------

    def submit_background(
        self,
        coro: Awaitable[Any],
        *,
        name: Optional[str] = None,
    ) -> str:
        """Fire-and-forget background work attached to this agent instance."""
        task_id = name or f"bg_{uuid.uuid4().hex[:8]}"
        task = asyncio.create_task(self._wrap_background(coro, task_id), name=task_id)
        self._background_tasks[task_id] = task
        task.add_done_callback(lambda t: self._background_tasks.pop(task_id, None))
        return task_id

    async def _wrap_background(self, coro: Awaitable[Any], task_id: str) -> Any:
        try:
            return await coro
        except Exception as exc:  # noqa: BLE001
            logger.exception("Background task %s failed on agent %s: %s", task_id, self.name, exc)
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_result(self, raw: Any, *, task_id: str) -> AgentResult:
        if isinstance(raw, AgentResult):
            if raw.task_id is None:
                raw.task_id = task_id
            return raw
        if isinstance(raw, dict):
            status_str = str(raw.get("status", AgentStatus.SUCCESS.value)).upper()
            try:
                status = AgentStatus(status_str)
            except ValueError:
                status = AgentStatus.SUCCESS
            return AgentResult(
                agent=self.name,
                status=status,
                output=raw.get("output", raw),
                next_agents=list(raw.get("next_agents") or raw.get("dispatch") or []),
                requires_human_review=bool(raw.get("requires_human_review")),
                task_id=task_id,
                metadata={k: v for k, v in raw.items() if k not in {
                    "status", "output", "next_agents", "dispatch", "requires_human_review"
                }},
            )
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output=raw,
            task_id=task_id,
        )

    async def _classify_and_recover(
        self,
        exc: Exception,
        *,
        task_id: str,
    ) -> AgentResult:
        """Map exceptions to anomaly tiers and decide log vs rollback."""
        tier = AnomalyTier.WARNING
        msg = str(exc)
        lower = msg.lower()
        if any(k in lower for k in ("auth", "permission", "secret", "payment", "webhook", "external")):
            tier = AnomalyTier.CRITICAL
        elif isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
            tier = AnomalyTier.WARNING

        logger.error(
            "Agent %s anomaly tier=%s task_id=%s: %s",
            self.name,
            tier.value,
            task_id,
            msg,
            exc_info=tier == AnomalyTier.CRITICAL,
        )

        if tier == AnomalyTier.CRITICAL:
            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILED,
                output={"error": msg, "rollback": True},
                anomaly_tier=tier,
                requires_human_review=True,
                task_id=task_id,
            )

        # Soft recovery path
        return AgentResult(
            agent=self.name,
            status=AgentStatus.RECOVERED,
            output={"error": msg, "recovered": True},
            anomaly_tier=tier,
            recovered_from_failure=True,
            task_id=task_id,
        )

    async def _log_memory(self, utterance: str, result: AgentResult) -> None:
        try:
            await self.memory.log_interaction(
                agent=self.name,
                utterance=utterance,
                result=result.to_dict(),
                tenant_id=self.tenant_id,
            )
        except Exception as exc:  # noqa: BLE001 — memory must never break the loop
            logger.warning("Memory log failed for agent %s: %s", self.name, exc)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} policy={self.default_policy!r}>"
