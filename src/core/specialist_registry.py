# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Capability → Agent registry for EliteRouter.
# Single source of truth for routing. Never free-form agent chat.

from __future__ import annotations

from typing import Any, Dict, Optional


CAPABILITY_MAP: Dict[str, str] = {
    # Core pipeline
    "intent.parse": "saphira",
    "persona.surface": "saphira",
    "perception.entity": "aura",
    "perception.scene": "aura",
    "vision.context": "aura",
    "security.gate": "agent_two",
    "policy.evaluate": "agent_two",
    "threat.scan": "agent_two",
    "governance.plan": "novareign",
    "dispatch.specialists": "novareign",
    "policy.enforce": "novareign",
    "memory.read": "novaaethrea",
    "memory.write": "novaaethrea",
    "memory.consolidate": "novaaethrea",
    "scene.expand": "novaaethrea",
    "device.execute": "agent_zero",
    "iot.control": "agent_zero",
    "node.invoke": "agent_zero",
    "tool.run": "agent_zero",
    # Specialists
    "strategy.revenue": "apex",
    "capital.allocate": "apex",
    "growth.channel": "apex",
    "sentiment.analyze": "instinct",
    "trend.detect": "instinct",
    "brand.position": "instinct",
    "data.pipeline": "lyra",
    "finance.model": "lyra",
    "chart.generate": "lyra",
    "compliance.audit": "lexis",
    "contract.review": "lexis",
    "legal.risk": "lexis",
    "infra.optimize": "cipher",
    "latency.reduce": "cipher",
    "reliability.harden": "cipher",
    "research.synthesize": "scholar",
    "playbook.create": "scholar",
    "knowledge.distill": "scholar",
}


class SpecialistRegistry:
    """Maps capability strings to live agent instances."""

    def __init__(self):
        self._agents: Dict[str, Any] = {}

    def register(self, key: str, agent: Any) -> None:
        self._agents[key] = agent

    def get(self, key: str) -> Optional[Any]:
        return self._agents.get(key)

    def agent_for(self, capability: str) -> str:
        return CAPABILITY_MAP.get(capability, "saphira")

    def all_keys(self) -> list:
        return list(self._agents.keys())
