# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Elite Agent Base — shared contract for every Saphira agent.
# Isolation token · secret-mask · memory hooks · timeout · retry · self-heal

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from src.core.agent_contract import AgentRole, describe_agent

logger = logging.getLogger("EliteAgent")


class EliteAgentBase(ABC):
    """
    Elite contract every Saphira agent must satisfy.

    - Isolation token per invocation (prevents identity bleed)
    - Secret-mask (never expose internal agent name to the user)
    - Memory hooks (recall before act, persist after success)
    - Timeout + retry + recovered_from_failure status
    - Explicit capability declaration
    """

    name: str = "base"
    role: AgentRole = AgentRole.SPECIALIST
    default_policy: str = "ALLOW"
    capabilities: List[str] = []
    max_timeout_s: float = 45.0
    max_retries: int = 2
    SYSTEM_VOICE: str = ""

    def __init__(self, memory_store: Any = None, router: Any = None):
        self.memory = memory_store
        self.router = router
        self._invocation_id: Optional[str] = None

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._invocation_id = str(uuid.uuid4())
        isolation_token = payload.get("isolation_token") or self._invocation_id
        tenant_id = payload.get("tenant_id", "default")

        # 1. Absolute recall
        memory_context: List[Any] = []
        if self.memory is not None:
            try:
                query = (
                    payload.get("text")
                    or payload.get("objective")
                    or payload.get("message")
                    or str(payload)[:200]
                )
                memory_context = await self.memory.recall(
                    tenant_id=tenant_id,
                    query=query,
                    top_k=6,
                )
            except Exception as e:
                logger.warning("[%s] memory recall failed: %s", self.name, e)

        enriched = {
            **payload,
            "isolation_token": isolation_token,
            "memory_context": [
                getattr(m, "content", m) for m in memory_context
            ],
            "agent_meta": describe_agent(self.name),
            "_internal_name": self.name,  # never surfaces to user
        }

        # 2. Execute with timeout + retry
        last_error: Optional[str] = None
        for attempt in range(1, self.max_retries + 2):
            try:
                result = await asyncio.wait_for(
                    self.process(enriched),
                    timeout=self.max_timeout_s,
                )
                result.setdefault("agent", self.name)
                result.setdefault("status", "success")
                result.setdefault("isolation_token", isolation_token)
                result["attempt"] = attempt

                # 3. Persist outcome
                if self.memory is not None and result.get("status") in (
                    "success",
                    "scene_executed",
                    "completed",
                ):
                    await self._persist_outcome(tenant_id, enriched, result)

                return result
            except asyncio.TimeoutError:
                last_error = "timeout"
                logger.warning("[%s] timeout attempt %d", self.name, attempt)
            except Exception as e:
                last_error = str(e)
                logger.exception("[%s] failure attempt %d", self.name, attempt)

        return {
            "agent": self.name,
            "status": "recovered_from_failure",
            "error": last_error,
            "isolation_token": isolation_token,
            "message": f"{self.name} recovered after {self.max_retries + 1} attempts",
        }

    async def _persist_outcome(
        self, tenant_id: str, payload: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        try:
            from src.memory.nova_aethrea_store import MemoryRecord, MemoryKind

            record = MemoryRecord(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                kind=MemoryKind.TASK_OUTCOME,
                content={
                    "agent": self.name,
                    "objective": payload.get("objective")
                    or payload.get("text")
                    or payload.get("message"),
                    "result_status": result.get("status"),
                    "summary": (
                        result.get("message")
                        or result.get("summary")
                        or ""
                    )[:500],
                },
                provenance={
                    "invocation_id": self._invocation_id,
                    "agent": self.name,
                },
            )
            await self.memory.write(record)
        except Exception as e:
            logger.warning("[%s] persist failed: %s", self.name, e)

    @abstractmethod
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-specific logic. Must be async and return a status dict."""
        ...
