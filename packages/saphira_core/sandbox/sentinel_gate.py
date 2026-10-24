# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Sentinel gate — maps Meta-style Sentinel guardrails onto Agent Cipher.

Every external action (browser navigate, form fill, payment, credential use,
account modification) must pass through this gate before the sandbox executes.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern

logger = logging.getLogger("saphira.sandbox.sentinel")


class SentinelVerdict(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"
    BLOCK_INJECTION = "BLOCK_INJECTION"


@dataclass
class SentinelDecision:
    verdict: SentinelVerdict
    reason: str
    action_summary: str
    risk_signals: List[str] = field(default_factory=list)
    requires_user_prompt: bool = False
    sanitized_payload: Optional[Dict[str, Any]] = None


# Heuristic patterns that commonly appear in prompt-injection payloads
# delivered via web pages, emails, or scraped content.
_INJECTION_PATTERNS: List[Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
    re.compile(r"system\s*prompt\s*[:=]", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.I),
    re.compile(r"disregard\s+(your|the)\s+(rules|guidelines|safety)", re.I),
    re.compile(r"<\s*/?\s*system\s*>", re.I),
    re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", re.I),
    re.compile(r"do\s+not\s+follow\s+your\s+original\s+instructions", re.I),
]


_CRITICAL_ACTION_TYPES = {
    "payment",
    "purchase",
    "transfer",
    "send_email",
    "account_modify",
    "password_change",
    "delete_account",
    "deploy_prod",
    "credential_export",
}


def _scan_for_injection(text: str) -> List[str]:
    hits: List[str] = []
    if not text:
        return hits
    for pat in _INJECTION_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def review_action(
    action: Dict[str, Any],
    *,
    page_content: Optional[str] = None,
    user_confirmed: bool = False,
) -> SentinelDecision:
    """
    Primary entry point used by Agent Cipher and the executive router.

    Parameters
    ----------
    action :
        Canonical action envelope, e.g.
        {
          "type": "browser.fill_form" | "payment" | "navigate" | ...,
          "url": "...",
          "payload": {...},
          "credential_refs": ["cred_email_..."],
        }
    page_content :
        Optional scraped page / email text to scan for injection.
    user_confirmed :
        True when the user has already approved a REQUIRE_APPROVAL decision.
    """
    action_type = str(action.get("type", "unknown")).lower()
    url = str(action.get("url", ""))
    payload = action.get("payload") or {}
    summary = f"{action_type} → {url or payload.get('target', 'local')}"

    risk_signals: List[str] = []

    # 1. Prompt-injection scan on any external content
    injection_hits = _scan_for_injection(page_content or "")
    if injection_hits:
        logger.warning("sentinel.injection_blocked hits=%s", injection_hits)
        return SentinelDecision(
            verdict=SentinelVerdict.BLOCK_INJECTION,
            reason="Potential prompt-injection payload detected in external content",
            action_summary=summary,
            risk_signals=injection_hits,
            requires_user_prompt=False,
        )

    # 2. Critical actions always require explicit user confirmation
    if action_type in _CRITICAL_ACTION_TYPES or any(
        k in action_type for k in ("pay", "purchase", "transfer", "delete")
    ):
        if not user_confirmed:
            return SentinelDecision(
                verdict=SentinelVerdict.REQUIRE_APPROVAL,
                reason="Critical action requires explicit user confirmation",
                action_summary=summary,
                risk_signals=["critical_action"],
                requires_user_prompt=True,
            )

    # 3. Credential usage is allowed only with a valid opaque ref
    cred_refs = action.get("credential_refs") or []
    if cred_refs and not all(str(r).startswith("cred_") for r in cred_refs):
        return SentinelDecision(
            verdict=SentinelVerdict.DENY,
            reason="Malformed credential reference — zero-trust policy violated",
            action_summary=summary,
            risk_signals=["invalid_credential_ref"],
        )

    # 4. Untrusted schemes
    if url and not url.startswith(("http://", "https://", "about:blank")):
        return SentinelDecision(
            verdict=SentinelVerdict.DENY,
            reason="Disallowed URL scheme",
            action_summary=summary,
            risk_signals=["bad_scheme"],
        )

    return SentinelDecision(
        verdict=SentinelVerdict.ALLOW,
        reason="Passed Sentinel heuristic and policy checks",
        action_summary=summary,
        risk_signals=risk_signals,
        sanitized_payload=payload if isinstance(payload, dict) else None,
    )
