# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Agent Cipher — System Architect + Sentinel Gatekeeper.

Maps Meta-style Sentinel guardrails onto the Nova Umbrella pipeline.
Every external web interaction, form fill, payment, or credential use is
routed through Cipher before the isolated sandbox executes it.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("saphira.agent.cipher")


class CipherAgent:
    name = "cipher"
    default_policy = "REQUIRE_APPROVAL"  # elevated from previous ALLOW

    def __init__(self) -> None:
        self._review_action = None
        self._SentinelVerdict = None
        self._vault = None
        self._driver = None
        self._CredentialKind = None

    def _lazy_imports(self) -> None:
        if self._review_action is not None:
            return
        try:
            from packages.saphira_core.sandbox.sentinel_gate import (
                review_action,
                SentinelVerdict,
            )
            from packages.saphira_core.sandbox.credential_vault import (
                credential_vault,
                CredentialKind,
            )
            from packages.saphira_core.sandbox.browser_driver import browser_driver

            self._review_action = review_action
            self._SentinelVerdict = SentinelVerdict
            self._vault = credential_vault
            self._driver = browser_driver
            self._CredentialKind = CredentialKind
        except ImportError as exc:
            logger.warning("Cipher sandbox imports unavailable: %s", exc)

    # ------------------------------------------------------------------
    # Legacy optimise surface (kept for compatibility)
    # ------------------------------------------------------------------
    def optimize(self, system: str) -> dict:
        return {
            "agent": self.name,
            "system": system,
            "plan": "profile → patch → CI",
            "sentinel": "active",
        }

    # ------------------------------------------------------------------
    # Sentinel gate (primary new surface)
    # ------------------------------------------------------------------
    def gate(
        self,
        action: Dict[str, Any],
        *,
        page_content: Optional[str] = None,
        user_confirmed: bool = False,
    ) -> Dict[str, Any]:
        """
        Review an external action before sandbox execution.

        Returns a decision envelope that the executive router must honour.
        """
        self._lazy_imports()
        if self._review_action is None:
            # Fail-closed when the sandbox package is missing
            return {
                "agent": self.name,
                "verdict": "DENY",
                "reason": "Sentinel gate unavailable — fail closed",
                "action": action,
            }

        decision = self._review_action(
            action,
            page_content=page_content,
            user_confirmed=user_confirmed,
        )
        return {
            "agent": self.name,
            "verdict": decision.verdict.value,
            "reason": decision.reason,
            "action_summary": decision.action_summary,
            "risk_signals": decision.risk_signals,
            "requires_user_prompt": decision.requires_user_prompt,
            "sanitized_payload": decision.sanitized_payload,
        }

    # ------------------------------------------------------------------
    # Zero-trust credential helpers
    # ------------------------------------------------------------------
    def register_credential(
        self,
        kind: str,
        label: str,
        value: str,
        *,
        domain_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._lazy_imports()
        if self._vault is None:
            return {"status": "error", "message": "Credential vault unavailable"}
        try:
            kind_enum = self._CredentialKind(kind)
        except (ValueError, TypeError):
            kind_enum = self._CredentialKind.OTHER
        ref = self._vault.register(
            kind_enum, label, value, domain_hint=domain_hint
        )
        return {
            "status": "ok",
            "ref_id": ref.ref_id,
            "kind": ref.kind.value,
            "label": ref.label,
            "domain_hint": ref.domain_hint,
            # Never return the raw value
        }

    def list_credentials(self) -> List[Dict[str, Any]]:
        self._lazy_imports()
        if self._vault is None:
            return []
        return [
            {
                "ref_id": r.ref_id,
                "kind": r.kind.value,
                "label": r.label,
                "domain_hint": r.domain_hint,
            }
            for r in self._vault.list_refs()
        ]

    # ------------------------------------------------------------------
    # Sandbox session helpers (delegates to BrowserDriver)
    # ------------------------------------------------------------------
    def open_sandbox(self, *, keep_alive: bool = False) -> Dict[str, Any]:
        self._lazy_imports()
        if self._driver is None:
            return {"status": "error", "message": "Browser driver unavailable"}
        session = self._driver.create_session(keep_alive=keep_alive)
        return {
            "status": "ok",
            "session_id": session.session_id,
            "mode": session.mode.value,
            "isolation": session.metadata.get("isolation"),
        }

    def close_sandbox(self, session_id: str) -> Dict[str, Any]:
        self._lazy_imports()
        if self._driver is None:
            return {"status": "error", "message": "Browser driver unavailable"}
        self._driver.close_session(session_id)
        return {"status": "ok", "session_id": session_id}
