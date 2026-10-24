# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Shared contract: anatomy, pillars, loop + Nova ecosystem classification
# Purpose binds every agent: compute patterns, automate tasks, solve at scale.

from typing import Dict, Any, List
from enum import Enum


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    EXECUTION = "execution"
    AUDITOR = "auditor"
    PERCEPTION = "perception"
    GOVERNANCE = "governance"
    MEMORY = "memory"
    SPECIALIST = "specialist"
    CREATIVE = "creative"


class AgentPillars:
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


# Canonical purpose string shared by every agent in the ecosystem
AI_PURPOSE = (
    "AI exists to compute patterns, automate tasks, and solve problems faster "
    "than human brains can alone. Automate complex cognitive tasks, analyze vast "
    "datasets, and solve problems at scale to augment human capabilities. Process "
    "information faster and more accurately so humans can leave repetitive labor, "
    "accelerate discovery, and improve decisions. Empower professionals to focus "
    "on higher-level strategy while AI handles time-consuming analysis. Foster "
    "collaboration between human intelligence and machine learning for solutions "
    "previously unimaginable."
)

SAPHIRA_ROLE_MAP = {
    "saphira": AgentRole.ORCHESTRATOR,
    "agent_zero": AgentRole.EXECUTION,
    "agent_two": AgentRole.AUDITOR,
    "aura": AgentRole.PERCEPTION,
    "nova_reign": AgentRole.GOVERNANCE,
    "nova_aethrea": AgentRole.MEMORY,
    "lyra": AgentRole.CREATIVE,
}


def describe_agent(name: str) -> Dict[str, Any]:
    role = SAPHIRA_ROLE_MAP.get(name, AgentRole.SPECIALIST)
    out: Dict[str, Any] = {
        "name": name,
        "role": role.value,
        "model_vs_agent": "agent",
        "purpose": AI_PURPOSE,
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
    try:
        from src.core.agent_classification import classify_core_agent

        out["classification"] = classify_core_agent(name)
    except Exception:
        out["classification"] = None
    return out


def perception_pipeline_note() -> str:
    return (
        "Raw input → tokenize/encode → embeddings → reason over goals. "
        "No biological emotion; optimization via task success + safety constraints. "
        "Purpose: compute patterns and automate cognitive work at scale."
    )
