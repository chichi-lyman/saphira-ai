# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Shared contract for every Saphira agent: anatomy, pillars, loop.

from typing import Dict, Any, List, Optional
from enum import Enum


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    EXECUTION = "execution"
    AUDITOR = "auditor"
    PERCEPTION = "perception"
    GOVERNANCE = "governance"
    MEMORY = "memory"
    SPECIALIST = "specialist"


class AgentPillars:
    """The four structural pillars required for continuous operation."""

    COMPUTE = "compute"
    MEMORY = "memory"
    TOOLS = "tools"
    GUARDRAILS = "guardrails"

    @staticmethod
    def checklist() -> List[str]:
        return [
            AgentPillars.COMPUTE,
            AgentPillars.MEMORY,
            AgentPillars.TOOLS,
            AgentPillars.GUARDRAILS,
        ]


# Canonical mapping: Saphira roster → taxonomy role
SAPHIRA_ROLE_MAP = {
    "saphira": AgentRole.ORCHESTRATOR,
    "agent_zero": AgentRole.EXECUTION,
    "agent_two": AgentRole.AUDITOR,
    "aura": AgentRole.PERCEPTION,
    "nova_reign": AgentRole.GOVERNANCE,
    "nova_aethrea": AgentRole.MEMORY,
}


def describe_agent(name: str) -> Dict[str, Any]:
    role = SAPHIRA_ROLE_MAP.get(name, AgentRole.SPECIALIST)
    return {
        "name": name,
        "role": role.value,
        "model_vs_agent": "agent",  # all Saphira units are agents (model + loop)
        "pillars_required": AgentPillars.checklist(),
        "loop": [
            "observe",
            "plan",
            "act_or_delegate",
            "verify",
            "remember",
            "report",
        ],
        "owner": "Chelsea Megan Woods",
        "studio": "Woods AI Studio / Lyman Legacies",
    }


def perception_pipeline_note() -> str:
    return (
        "Raw input → tokenize/encode → embeddings → reason over goals. "
        "No biological emotion; optimization via task success + safety constraints."
    )
