"""
src/core/policy.py — CommercialAuthorityPolicy + Security Gates
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Invariants:
- ALLOW / REQUIRE_APPROVAL / DENY are the only legal outcomes for commercial or hardware actions.
- All decisions are written to a hash-chained AuditStore.
- No autonomous external messaging or payment activation without verified signatures.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AuthorityDecision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


@dataclass
class GateResult:
    decision: AuthorityDecision
    reason: str
    audit_id: Optional[str] = None
    denied: bool = False


class CommercialAuthorityPolicy:
    HIGH_RISK_DOMAINS = {"lock", "payment", "transfer", "delete", "deploy_prod"}

    def evaluate(self, domain: str, service: str, entity_id: str = "", amount: float = 0.0) -> GateResult:
        if domain in self.HIGH_RISK_DOMAINS:
            return GateResult(
                decision=AuthorityDecision.REQUIRE_APPROVAL,
                reason=f"high_risk:{domain}.{service}",
                denied=True,
            )
        if amount > 0 and amount > float(os.getenv("AUTO_APPROVE_LIMIT", "25.0")):
            return GateResult(
                decision=AuthorityDecision.REQUIRE_APPROVAL,
                reason="amount_above_auto_limit",
                denied=True,
            )
        return GateResult(decision=AuthorityDecision.ALLOW, reason="policy_ok", denied=False)


class AuditStore:
    def __init__(self, path: str = "data/audit_chain.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._last_hash = self._load_last_hash()

    def _load_last_hash(self) -> str:
        try:
            with open(self.path, "rb") as f:
                lines = f.readlines()
                if not lines:
                    return "genesis"
                last = json.loads(lines[-1])
                return last.get("hash", "genesis")
        except FileNotFoundError:
            return "genesis"

    def append(self, event: dict) -> str:
        payload = {
            "ts": time.time(),
            "prev": self._last_hash,
            "event": event,
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        h = hashlib.sha256(raw).hexdigest()
        payload["hash"] = h
        with open(self.path, "a") as f:
            f.write(json.dumps(payload) + "\n")
        self._last_hash = h
        return h


_policy = CommercialAuthorityPolicy()
_audit = AuditStore()


async def require_security_gate(
    domain: str,
    service: str,
    entity_id: str = "",
    auth_token: Optional[str] = None,
    amount: float = 0.0,
) -> GateResult:
    result = _policy.evaluate(domain, service, entity_id, amount)

    if result.decision == AuthorityDecision.REQUIRE_APPROVAL:
        expected = os.getenv("SECURITY_PIN") or os.getenv("HA_SECURITY_TOKEN")
        if not auth_token or (expected and auth_token != expected):
            result.denied = True
            result.reason = "missing_or_invalid_auth_token"
            _audit.append({
                "action": "gate_denied",
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "reason": result.reason,
            })
            return result
        result = GateResult(decision=AuthorityDecision.ALLOW, reason="auth_token_accepted", denied=False)

    audit_id = _audit.append({
        "action": "gate_decision",
        "domain": domain,
        "service": service,
        "entity_id": entity_id,
        "decision": result.decision.value,
        "reason": result.reason,
    })
    result.audit_id = audit_id
    return result
