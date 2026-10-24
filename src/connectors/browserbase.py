# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Browserbase connector — managed browser sessions for Google / Maps / complex sites.

Gives Agent Two (and other agents via the registry) reliable, isolated browser
contexts without maintaining local Playwright infrastructure.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


class BrowserbaseConnector:
    """Adapter for Browserbase managed browser / session APIs."""

    def __init__(self) -> None:
        self.api_key = os.getenv("BROWSERBASE_API_KEY", "")
        self.project_id = os.getenv("BROWSERBASE_PROJECT_ID", "")
        self.base_url = os.getenv("BROWSERBASE_BASE_URL", "https://www.browserbase.com/v1")

    def health(self) -> Dict[str, Any]:
        configured = bool(self.api_key and self.project_id)
        return {
            "status": "ready" if configured else "unconfigured",
            "provider": "browserbase",
            "capabilities": ("web.browse", "web.scrape", "browser.session"),
            "configured": configured,
        }

    def create_session(self, *, keep_alive: bool = False) -> Dict[str, Any]:
        """Create a managed browser session."""
        if not self.api_key or not self.project_id:
            return {
                "status": "error",
                "message": "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID required",
            }
        return {
            "status": "queued",
            "note": "Wire Browserbase /sessions for production session IDs and connect URLs",
            "provider": "browserbase",
            "project_id": self.project_id,
            "keep_alive": keep_alive,
            "session_id": None,
        }

    def navigate_and_extract(
        self,
        url: str,
        *,
        session_id: Optional[str] = None,
        wait_for: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Navigate to a URL inside a managed session and return clean text / DOM summary."""
        if not self.api_key or not self.project_id:
            return {
                "status": "error",
                "message": "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID required",
            }
        if not url.strip().startswith(("http://", "https://")):
            return {"status": "error", "message": "URL must be http(s)"}
        return {
            "status": "queued",
            "note": "Wire Browserbase session + Playwright-compatible commands for extraction",
            "provider": "browserbase",
            "url": url.strip(),
            "session_id": session_id,
            "wait_for": wait_for,
            "content": "",
        }
