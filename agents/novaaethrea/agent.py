# Copyright © 2026 Chelsea Megan Woods
"""NovaAethrea — memory and connectivity."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class NovaAethreaAgent(BaseAgent):
    name = "novaaethrea"
    description = "Memory, context continuity, and connectivity"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        prior = await self.memory.recall(utterance, limit=3, tenant_id=self.tenant_id)
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"recalled": prior, "stabilized": True},
            next_agents=["agent_zero"],
        )
