# Copyright © 2026 Chelsea Megan Woods
"""NovaReign — governance and specialist dispatch."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class NovaReignAgent(BaseAgent):
    name = "novareign"
    description = "Governance and strategic dispatch"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"goal": utterance, "dispatch_plan": ["instinct", "apex", "scholar"]},
            next_agents=["novaaethrea", "instinct", "apex", "scholar"],
        )
