# Copyright © 2026 Chelsea Megan Woods
"""Adaptive multi-domain cognitive training — mode switch and ethical audit hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CognitiveMode(str, Enum):
    ADVISOR = "empathetic_strategic_advisor"
    RED_TEAM = "aggressive_red_teamer"
    EXECUTION = "execution_pipeline"
    TRANSLATOR = "behavioral_contextual_translator"
    MEMORY = "memory_continuity"
    ANALYTICS = "analytics_truth"


@dataclass
class DialecticalPass:
    """Yin–Yang: optimistic design + pessimistic risk."""

    proposal: str
    risks: list[str] = field(default_factory=list)
    assumptions_challenged: list[str] = field(default_factory=list)
    revised: str | None = None

    def balance(self) -> dict[str, Any]:
        return {
            "proposal": self.proposal,
            "risks": self.risks or ["Unstated risk: impact on real humans not listed"],
            "assumptions_challenged": self.assumptions_challenged,
            "revised": self.revised or self.proposal,
            "method": "dialectical_yin_yang",
        }


@dataclass
class EthicalAudit:
    """Compassion-anchored check before final recommendations."""

    action: str
    safety_ok: bool = True
    bias_notes: list[str] = field(default_factory=list)
    human_impact: str = ""
    block: bool = False
    reason: str = ""

    def run(self) -> dict[str, Any]:
        # Hard blocks only for severe harm classes; owner ALLOW does not override these.
        lower = self.action.lower()
        hard = any(
            k in lower
            for k in (
                "self-harm",
                "suicide method",
                "how to kill",
                "child sexual",
                "build a bomb",
            )
        )
        if hard:
            self.block = True
            self.safety_ok = False
            self.reason = "Hard ethical boundary"
        return {
            "action": self.action,
            "safety_ok": self.safety_ok,
            "bias_notes": self.bias_notes,
            "human_impact": self.human_impact or "Consider real-world effect on people",
            "block": self.block,
            "reason": self.reason,
            "principle": "compassion",
        }


def select_mode(user_intent: str) -> CognitiveMode:
    t = user_intent.lower()
    if any(w in t for w in ("risk", "secure", "threat", "red team", "attack", "compliance")):
        return CognitiveMode.RED_TEAM
    if any(w in t for w in ("build", "deploy", "ship", "schedule", "execute", "automate", "post")):
        return CognitiveMode.EXECUTION
    if any(w in t for w in ("metric", "number", "chart", "analytics", "roi")):
        return CognitiveMode.ANALYTICS
    if any(w in t for w in ("remember", "context", "last time", "history")):
        return CognitiveMode.MEMORY
    if any(w in t for w in ("tone", "mean", "rephrase", "audience", "prompt")):
        return CognitiveMode.TRANSLATOR
    return CognitiveMode.ADVISOR


def train_pass(user_intent: str, draft: str) -> dict[str, Any]:
    """One training-shaped cycle: mode → dialectic → ethics → output."""
    mode = select_mode(user_intent)
    dial = DialecticalPass(
        proposal=draft,
        risks=["Normative average response risk"],
        assumptions_challenged=["User prompt may contain hidden constraints"],
    ).balance()
    ethics = EthicalAudit(action=draft, human_impact="User and audience wellbeing").run()
    return {
        "mode": mode.value,
        "dialectical": dial,
        "ethical_audit": ethics,
        "outcomes": [
            "eliminate_normative_average",
            "maximize_utility_across_tasks",
            "prevent_blind_automation",
        ],
        "framework": "Woods adaptive multi-domain cognitive engine",
    }
