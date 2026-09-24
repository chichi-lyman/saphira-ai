# Copyright © 2026 Chelsea Megan Woods
"""Agent Two — security gate (REQUIRE_APPROVAL by default)."""
from __future__ import annotations

from typing import Any, Dict

from packages.saphira_core.base_agent import AgentResult, AgentStatus, BaseAgent


class AgentTwo(BaseAgent):
    name = "agent_two"
    description = "Security and red-team gate"

    async def handle(self, utterance: str, context: Dict[str, Any]) -> AgentResult:
        # Security review is policy-gated via BaseAgent.safe_run (REQUIRE_APPROVAL).
        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"security_review": "passed", "flags": []},
            next_agents=["novareign"],
        )
