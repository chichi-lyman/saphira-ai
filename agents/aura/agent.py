# Copyright © 2026 Chelsea Megan Woods
"""Aura — perception and content."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class AuraAgent(BaseAgent):
    name = "aura"
    description = "Perception & content shaping"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"perception": utterance, "context_keys": list(context.keys())},
            next_agents=["agent_two"],
        )
