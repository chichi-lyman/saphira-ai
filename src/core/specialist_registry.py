# Copyright © 2026 Chelsea Megan Woods
# Capability registry for extended family specialists (Apex, Lexis, Instinct, Cipher, Scholar)
# Dispatched by NovaReign or SwarmOrchestrator.
#
# Owner policy (2026-09): Agent Apex and Agent Instinct are ALLOW for create/post
# without human approval. Other specialists retain prior defaults.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("SaphiraSpecialistRegistry")


@dataclass(frozen=True)
class SpecialistSpec:
    codename: str
    title: str
    domain: str
    default_policy: str  # ALLOW | REQUIRE_APPROVAL | DENY
    can_fan_out: bool = True
    description: str = ""


EXTENDED_SPECIALISTS: Dict[str, SpecialistSpec] = {
    "agent_apex": SpecialistSpec(
        codename="agent_apex",
        title="The Venture Strategist",
        domain="revenue_growth_capital_allocation",
        default_policy="ALLOW",
        description="Financial modeling, growth channels, and approved autonomous commercial/content actions per owner policy.",
    ),
    "agent_lexis": SpecialistSpec(
        codename="agent_lexis",
        title="The Regulatory Guardian",
        domain="compliance_contract_risk",
        default_policy="REQUIRE_APPROVAL",
        description="Contract and compliance risk scanning; no formal legal advice.",
    ),
    "agent_instinct": SpecialistSpec(
        codename="agent_instinct",
        title="The Market and Consumer Whisperer",
        domain="sentiment_trends_positioning",
        default_policy="ALLOW",
        description="Sentiment, trends, and autonomous content creation/publishing per owner policy.",
    ),
    "agent_cipher": SpecialistSpec(
        codename="agent_cipher",
        title="The System Architect and Optimizer",
        domain="infrastructure_latency_reliability",
        default_policy="ALLOW",
        description="Performance and reliability plans; production changes via Agent Zero + CI.",
    ),
    "agent_scholar": SpecialistSpec(
        codename="agent_scholar",
        title="The Rapid Knowledge Synthesizer",
        domain="research_playbooks_training",
        default_policy="ALLOW",
        description="Ordered playbooks and first-principles guides from dense material.",
    ),
    "lyra": SpecialistSpec(
        codename="lyra",
        title="Numbers and Charts",
        domain="data_finance_analytics",
        default_policy="REQUIRE_APPROVAL",
        description="Transparent models and charts; financial outputs that move spend still prefer review unless owner expands ALLOW.",
    ),
}


class SpecialistCapabilityRegistry:
    """In-process registry of extended specialists for NovaReign fan-out."""

    def __init__(self) -> None:
        self._impls: Dict[str, Any] = {}
        self._specs = dict(EXTENDED_SPECIALISTS)

    def register(self, codename: str, implementation: Any) -> None:
        if codename not in self._specs:
            logger.warning("Registering unknown specialist codename: %s", codename)
        self._impls[codename] = implementation

    def get_spec(self, codename: str) -> Optional[SpecialistSpec]:
        return self._specs.get(codename)

    def list_specs(self) -> List[SpecialistSpec]:
        return list(self._specs.values())

    def get_implementation(self, codename: str) -> Optional[Any]:
        return self._impls.get(codename)

    def available_for_dispatch(self) -> List[str]:
        return [c for c in self._specs if c in self._impls]

    def policy_for(self, codename: str) -> str:
        spec = self._specs.get(codename)
        return spec.default_policy if spec else "REQUIRE_APPROVAL"


specialist_registry = SpecialistCapabilityRegistry()
