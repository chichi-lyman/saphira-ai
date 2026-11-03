"""
agents/agent_two/agent.py — Security & L1 policy gates
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Integrates src/core/policy.py :: require_security_gate / CommercialAuthorityPolicy.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("saphira.agent_two")


@dataclass
class GateResult:
    denied: bool
    reason: str = ""
    decision: str = "ALLOW"
    audit_id: Optional[str] = None


_HIGH_RISK_PATTERNS = [
    re.compile(r"\b(unlock|open the door|disarm)\b", re.I),
    re.compile(r"\b(pay|transfer|send money|purchase|buy now)\b", re.I),
    re.compile(r"\b(delete (all|everything|production|prod)|drop database|rm -rf)\b", re.I),
    re.compile(r"\b(deploy to prod|deploy production)\b", re.I),
]


def _text_of(intent: Any) -> str:
    if intent is None:
        return ""
    if hasattr(intent, "text"):
        return str(intent.text or "")
    if hasattr(intent, "raw"):
        return str(intent.raw or "")
    if isinstance(intent, dict):
        return str(intent.get("text") or intent.get("message") or "")
    return str(intent)


def _domain_from_intent(intent: Any, perception: Optional[dict] = None) -> tuple[str, str, str]:
    text = _text_of(intent).lower()
    perception = perception or {}
    if any(w in text for w in ("unlock", "lock", "door")):
        return "lock", "unlock" if "unlock" in text else "lock", perception.get("entity_id", "")
    if any(w in text for w in ("pay", "transfer", "purchase", "buy")):
        return "payment", "charge", ""
    if "delete" in text or "drop database" in text:
        return "delete", "destroy", ""
    if "deploy" in text and "prod" in text:
        return "deploy_prod", "deploy", ""
    if any(w in text for w in ("cast", "tv", "chromecast")):
        return "media", "cast", perception.get("entity_id", "")
    return "general", "chat", ""


class AgentTwo:
    name = "agent_two"
    default_policy = "REQUIRE_APPROVAL"

    def gate(self, action: dict) -> dict:
        intent = action.get("intent") or action.get("goal") or action
        text = _text_of(intent)
        for pat in _HIGH_RISK_PATTERNS:
            if pat.search(text):
                return {
                    "agent": self.name,
                    "decision": "deny",
                    "reason": f"high_risk_pattern:{pat.pattern}",
                    "action": action,
                }
        return {"agent": self.name, "decision": "clear", "action": action}

    async def evaluate(self, intent: Any, perception: Optional[dict] = None) -> GateResult:
        perception = perception or {}
        text = _text_of(intent)

        for pat in _HIGH_RISK_PATTERNS:
            if pat.search(text):
                domain, service, entity_id = _domain_from_intent(intent, perception)
                return await self._policy_check(
                    domain=domain,
                    service=service,
                    entity_id=entity_id,
                    auth_token=perception.get("auth_token") or perception.get("pin"),
                    amount=float(perception.get("amount") or 0),
                )

        domain, service, entity_id = _domain_from_intent(intent, perception)
        if domain == "general":
            return GateResult(denied=False, reason="general_chat", decision="ALLOW")

        return await self._policy_check(
            domain=domain,
            service=service,
            entity_id=entity_id,
            auth_token=perception.get("auth_token") or perception.get("pin"),
            amount=float(perception.get("amount") or 0),
        )

    async def _policy_check(
        self,
        domain: str,
        service: str,
        entity_id: str = "",
        auth_token: Optional[str] = None,
        amount: float = 0.0,
    ) -> GateResult:
        try:
            from src.core.policy import require_security_gate

            result = await require_security_gate(
                domain=domain,
                service=service,
                entity_id=entity_id,
                auth_token=auth_token,
                amount=amount,
            )
            denied = bool(getattr(result, "denied", False))
            decision = getattr(result, "decision", None)
            decision_str = decision.value if hasattr(decision, "value") else str(decision or "ALLOW")
            return GateResult(
                denied=denied,
                reason=getattr(result, "reason", ""),
                decision=decision_str,
                audit_id=getattr(result, "audit_id", None),
            )
        except Exception as exc:
            logger.warning("policy module unavailable, failing closed for high-risk: %s", exc)
            if domain in {"lock", "payment", "transfer", "delete", "deploy_prod"}:
                return GateResult(
                    denied=True,
                    reason=f"policy_unavailable_fail_closed:{type(exc).__name__}",
                    decision="DENY",
                )
            return GateResult(denied=False, reason="policy_unavailable_allow_low_risk", decision="ALLOW")
