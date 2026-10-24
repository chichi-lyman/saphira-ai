"""Map internal agents to excellence pillars they own.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

# Internal codenames only — never surface these to end users.
AGENT_EXCELLENCE_MAP: dict[str, tuple[str, ...]] = {
    "saphira": ("latency", "memory", "privacy", "reasoning", "overall"),
    "agent_two": ("automation", "privacy"),
    "scholar": ("reasoning", "memory"),
    "novaaethrea": ("memory", "reasoning"),
    "novareign": ("privacy", "automation"),
    "aura": ("latency", "edge", "automation"),
    "agent_zero": ("edge", "latency"),
    "cipher": ("privacy", "edge"),
    "orchestrator": ("overall", "automation", "reasoning"),
}


def owners_for_pillar(pillar_id: str) -> list[str]:
    """Return internal agent keys that own a pillar."""
    return sorted(
        agent
        for agent, pillars in AGENT_EXCELLENCE_MAP.items()
        if pillar_id in pillars
    )


def pillars_for_agent(agent_key: str) -> tuple[str, ...]:
    return AGENT_EXCELLENCE_MAP.get(agent_key.lower(), ())
