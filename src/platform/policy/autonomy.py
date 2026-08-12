"""Autonomy levels and capability gating (L1 / L2 / L3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class AutonomyLevel(str, Enum):
    L1_CONFIRM_FIRST = "L1_confirm_first"
    L2_SUPERVISED = "L2_supervised"
    L3_BACKGROUND = "L3_background"


DEFAULT_L1_CAPABILITIES: Set[str] = {
    "payment",
    "unlock",
    "send_email",
    "cold_outreach",
    "deploy_prod",
    "delete_data",
    "wire_transfer",
    "share_credentials",
}


@dataclass
class AutonomyDecision:
    allowed: bool
    level: AutonomyLevel
    requires_confirmation: bool
    reason: str
    capability: str
    preview: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutonomyPolicy:
    """Per-tenant / per-user autonomy configuration."""

    tenant_id: str = "default"
    default_level: AutonomyLevel = AutonomyLevel.L2_SUPERVISED
    l1_capabilities: Set[str] = field(default_factory=lambda: set(DEFAULT_L1_CAPABILITIES))
    l3_allowlist: Set[str] = field(default_factory=set)
    disabled_capabilities: Set[str] = field(default_factory=set)
    stress_raise_to_l1: bool = True

    def decide(self, capability: str, context: Optional[Dict[str, Any]] = None) -> AutonomyDecision:
        context = context or {}
        cap = capability.strip().lower()

        if cap in self.disabled_capabilities:
            return AutonomyDecision(
                allowed=False,
                level=self.default_level,
                requires_confirmation=False,
                reason="Capability disabled by policy",
                capability=cap,
            )

        stress = (context.get("stress_level") or "").lower()
        force_l1 = bool(context.get("force_l1")) or (
            getattr(self, "stress_raise_to_l1", True) and stress in ("high", "critical")
        )
        if cap in self.l1_capabilities or force_l1:
            return AutonomyDecision(
                allowed=True,
                level=AutonomyLevel.L1_CONFIRM_FIRST,
                requires_confirmation=not bool(context.get("confirmed")),
                reason="L1 capability requires explicit confirmation" if not force_l1 else "Elevated to L1 due to high user stress or force flag",
                capability=cap,
                preview={
                    "capability": cap,
                    "side_effects": context.get("side_effects", []),
                    "rollback": context.get("rollback"),
                },
            )

        if cap in self.l3_allowlist:
            return AutonomyDecision(
                allowed=True,
                level=AutonomyLevel.L3_BACKGROUND,
                requires_confirmation=False,
                reason="Capability on L3 allowlist",
                capability=cap,
            )

        return AutonomyDecision(
            allowed=True,
            level=self.default_level,
            requires_confirmation=self.default_level == AutonomyLevel.L1_CONFIRM_FIRST,
            reason="Default tenant autonomy level",
            capability=cap,
        )


class CounterfactualPreview:
    """Build a human-readable approval preview before L1 execution."""

    @staticmethod
    def build(
        intent: str,
        capability: str,
        tools: List[str],
        side_effects: Optional[List[str]] = None,
        rollback: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "title": f"Confirm action: {capability}",
            "intent": intent,
            "capability": capability,
            "tools": tools,
            "side_effects": side_effects or [],
            "rollback": rollback or "Manual reversal required",
            "prompt": f"Saphira is about to execute '{capability}'. Please confirm or cancel.",
        }
