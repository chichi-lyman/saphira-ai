# Copyright © 2026 Chelsea Megan Woods
"""Monorepo specialist registry — mirrors pipeline agents under agents/."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AgentMeta:
    package: str
    title: str
    default_policy: str


AGENTS: Dict[str, AgentMeta] = {
    "saphira": AgentMeta("agents.saphira", "Surface Assistant", "ALLOW"),
    "aura": AgentMeta("agents.aura", "Perception & Content", "ALLOW"),
    "agent_two": AgentMeta("agents.agent_two", "Security Gate", "REQUIRE_APPROVAL"),
    "novareign": AgentMeta("agents.novareign", "Governance", "ALLOW"),
    "novaaethrea": AgentMeta("agents.novaaethrea", "Memory & Connectivity", "ALLOW"),
    "agent_zero": AgentMeta("agents.agent_zero", "Execution", "ALLOW"),
    "lyra": AgentMeta("agents.lyra", "Analytics", "REQUIRE_APPROVAL"),
    "apex": AgentMeta("agents.apex", "Venture Strategist", "ALLOW"),
    "instinct": AgentMeta("agents.instinct", "Market & Content", "ALLOW"),
    "lexis": AgentMeta("agents.lexis", "Regulatory Guardian", "REQUIRE_APPROVAL"),
    "cipher": AgentMeta("agents.cipher", "System Architect", "ALLOW"),
    "scholar": AgentMeta("agents.scholar", "Knowledge Synthesizer", "ALLOW"),
}


def list_agents() -> List[str]:
    return list(AGENTS.keys())


def policy_for(name: str) -> str:
    meta = AGENTS.get(name)
    return meta.default_policy if meta else "REQUIRE_APPROVAL"
