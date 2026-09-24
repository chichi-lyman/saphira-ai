# Copyright © 2026 Chelsea Megan Woods
"""Lyra — analytics (REQUIRE_APPROVAL)."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class LyraAgent(BaseAgent):
    name = "lyra"
    description = "Analytics and transparent metrics"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"metrics": {}, "note": "numbers without spin"},
            next_agents=[],
        )
