# © 2026 Chelsea Megan Woods
# Lean capability map — pure dict, no ceremony.

from __future__ import annotations
from typing import Any, Dict, Optional

CAPABILITY_MAP: Dict[str, str] = {
    "intent.parse": "saphira",
    "persona.surface": "saphira",
    "perception.entity": "aura",
    "perception.scene": "aura",
    "security.gate": "agent_two",
    "policy.evaluate": "agent_two",
    "governance.plan": "novareign",
    "dispatch.specialists": "novareign",
    "memory.read": "novaaethrea",
    "memory.write": "novaaethrea",
    "device.execute": "agent_zero",
    "iot.control": "agent_zero",
    "strategy.revenue": "apex",
    "capital.allocate": "apex",
    "sentiment.analyze": "instinct",
    "trend.detect": "instinct",
    "data.pipeline": "lyra",
    "finance.model": "lyra",
    "compliance.audit": "lexis",
    "legal.risk": "lexis",
    "infra.optimize": "cipher",
    "latency.reduce": "cipher",
    "research.synthesize": "scholar",
    "knowledge.distill": "scholar",
}

class SpecialistRegistry:
    __slots__ = ("_a",)

    def __init__(self):
        self._a: Dict[str, Any] = {}

    def register(self, key: str, agent: Any) -> None:
        self._a[key] = agent

    def get(self, key: str) -> Optional[Any]:
        return self._a.get(key)

    def agent_for(self, capability: str) -> str:
        return CAPABILITY_MAP.get(capability, "saphira")
