# Copyright © 2026 Chelsea Megan Woods
"""Lexis — regulatory guardian (REQUIRE_APPROVAL)."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class LexisAgent(BaseAgent):
    name = "lexis"
    description = "Compliance and regulatory risk (not formal legal advice)"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"risk_flags": [], "disclaimer": "Not formal legal advice"},
            next_agents=[],
        )
