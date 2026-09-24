# Copyright © 2026 Chelsea Megan Woods
"""Saphira — only user-facing surface (intent capture)."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class SaphiraAgent(BaseAgent):
    """Only user-facing voice. Routes work internally; never exposes pipeline."""

    name = "saphira"
    description = "Surface assistant — intent capture and user liaison"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"intent": utterance, "route": "pipeline"},
            next_agents=["aura"],
        )
