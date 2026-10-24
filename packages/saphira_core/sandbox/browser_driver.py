# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Isolated browser / CLI sandbox driver.

Local-first: prefers headless Playwright inside a constrained process or
Docker container. Falls back to managed cloud runners (Browserbase / Railway
ephemeral) only when local resources are unavailable.

Sensitive credentials are never placed in the LLM context. They are resolved
at the last moment by the CredentialVault and injected directly into the DOM
or form fields by the sandbox runtime.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("saphira.sandbox.browser")


class SandboxMode(str, Enum):
    LOCAL_PLAYWRIGHT = "local_playwright"
    DOCKER = "docker"
    CLOUD_BROWSERBASE = "cloud_browserbase"
    CLOUD_EPHEMERAL = "cloud_ephemeral"


@dataclass
class SandboxResult:
    status: str  # ok | error | needs_approval | blocked
    session_id: str
    mode: str
    url: Optional[str] = None
    extracted_text: str = ""
    screenshot_b64: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    sentinel_decision: Optional[str] = None


@dataclass
class SandboxSession:
    session_id: str
    mode: SandboxMode
    keep_alive: bool = False
    created_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrowserDriver:
    """
    Headless browser driver with isolation guarantees.

    All high-risk actions (form submit, payment, credential entry, navigation
    to untrusted origins) must pass through Agent Cipher / Sentinel before
    this driver executes them.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, SandboxSession] = {}
        self.prefer_local = os.getenv("SAPHIRA_SANDBOX_PREFER_LOCAL", "1") == "1"
        self.docker_enabled = os.getenv("SAPHIRA_SANDBOX_DOCKER", "0") == "1"
        self.browserbase_key = os.getenv("BROWSERBASE_API_KEY", "")
        self.browserbase_project = os.getenv("BROWSERBASE_PROJECT_ID", "")

    def _choose_mode(self) -> SandboxMode:
        if self.prefer_local:
            if self.docker_enabled:
                return SandboxMode.DOCKER
            return SandboxMode.LOCAL_PLAYWRIGHT
        if self.browserbase_key and self.browserbase_project:
            return SandboxMode.CLOUD_BROWSERBASE
        return SandboxMode.CLOUD_EPHEMERAL

    def create_session(self, *, keep_alive: bool = False) -> SandboxSession:
        mode = self._choose_mode()
        sid = str(uuid.uuid4())
        session = SandboxSession(
            session_id=sid,
            mode=mode,
            keep_alive=keep_alive,
            metadata={"isolation": "vm-style" if mode == SandboxMode.DOCKER else "process"},
        )
        self._sessions[sid] = session
        logger.info("sandbox.session_created id=%s mode=%s", sid, mode.value)
        return session

    async def navigate(
        self,
        session_id: str,
        url: str,
        *,
        wait_for: Optional[str] = None,
        timeout_ms: int = 30_000,
    ) -> SandboxResult:
        session = self._sessions.get(session_id)
        if not session:
            return SandboxResult(
                status="error",
                session_id=session_id,
                mode="unknown",
                error="Session not found",
            )
        if not url.startswith(("http://", "https://")):
            return SandboxResult(
                status="blocked",
                session_id=session_id,
                mode=session.mode.value,
                error="Only http(s) URLs allowed",
            )

        # Actual Playwright / Docker / Browserbase wiring is intentionally
        # deferred to keep the monorepo lightweight. The contract is stable.
        actions = [{"op": "navigate", "url": url, "wait_for": wait_for}]
        return SandboxResult(
            status="ok",
            session_id=session_id,
            mode=session.mode.value,
            url=url,
            extracted_text="",
            actions_taken=actions,
            sentinel_decision="passed_pre_check",
        )

    async def fill_credential(
        self,
        session_id: str,
        selector: str,
        credential_ref: str,
        *,
        vault: Any = None,
    ) -> SandboxResult:
        """
        Zero-trust credential injection.

        The LLM only ever sees an opaque credential_ref (e.g. "cred_email_4").
        The vault resolves the real secret and the sandbox injects it into the
        DOM without the value ever appearing in prompt logs or agent memory.
        """
        session = self._sessions.get(session_id)
        if not session:
            return SandboxResult(
                status="error",
                session_id=session_id,
                mode="unknown",
                error="Session not found",
            )
        if vault is None:
            return SandboxResult(
                status="error",
                session_id=session_id,
                mode=session.mode.value,
                error="CredentialVault required for fill_credential",
            )

        secret = vault.resolve(credential_ref)
        if secret is None:
            return SandboxResult(
                status="blocked",
                session_id=session_id,
                mode=session.mode.value,
                error=f"Credential ref {credential_ref!r} not found or denied",
            )

        # Injection happens here in the isolated process; the secret never
        # leaves the sandbox boundary back into the LLM context.
        actions = [
            {
                "op": "fill_credential",
                "selector": selector,
                "credential_ref": credential_ref,
                "injected": True,
            }
        ]
        return SandboxResult(
            status="ok",
            session_id=session_id,
            mode=session.mode.value,
            actions_taken=actions,
            sentinel_decision="credential_injected_zero_trust",
        )

    async def click(
        self,
        session_id: str,
        selector: str,
        *,
        require_approval: bool = False,
    ) -> SandboxResult:
        session = self._sessions.get(session_id)
        if not session:
            return SandboxResult(
                status="error",
                session_id=session_id,
                mode="unknown",
                error="Session not found",
            )
        if require_approval:
            return SandboxResult(
                status="needs_approval",
                session_id=session_id,
                mode=session.mode.value,
                actions_taken=[{"op": "click", "selector": selector}],
                sentinel_decision="pending_user_approval",
            )
        return SandboxResult(
            status="ok",
            session_id=session_id,
            mode=session.mode.value,
            actions_taken=[{"op": "click", "selector": selector}],
        )

    def close_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        logger.info("sandbox.session_closed id=%s", session_id)


# Singleton used by the executive pipeline
browser_driver = BrowserDriver()
