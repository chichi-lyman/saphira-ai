# Copyright © 2026 Chelsea Megan Woods
"""Publer connector — schedule and publish via Publer API v1 (Business).

Docs: https://app.publer.com/api/v1
Auth: Bearer token from Publer Business account (store as PUBLER_API_TOKEN secret).
"""

from __future__ import annotations

import os
from typing import Any, Optional
import httpx
import logging

logger = logging.getLogger("Saphira.Publer")

BASE_URL = os.getenv("PUBLER_API_BASE", "https://app.publer.com/api/v1")


class PublerConnector:
    name = "publer"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("PUBLER_API_TOKEN", "")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def configured(self) -> bool:
        return bool(self.token)

    async def schedule_post(
        self,
        *,
        text: str,
        accounts: list[str] | None = None,
        scheduled_at: str | None = None,
        media_urls: list[str] | None = None,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Schedule or queue a post. Returns job metadata or error stub if unconfigured."""
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set PUBLER_API_TOKEN secret to enable Publer scheduling",
                "payload_preview": {"text": text[:200], "scheduled_at": scheduled_at},
            }

        body: dict[str, Any] = {
            "text": text,
            "accounts": accounts or [],
            "media": media_urls or [],
        }
        if scheduled_at:
            body["scheduled_at"] = scheduled_at
        if draft:
            body["state"] = "draft"

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Endpoint shape may vary by Publer plan; treat as integration surface
            r = await client.post(
                f"{BASE_URL}/posts",
                headers=self._headers(),
                json=body,
            )
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text[:500]}
            return {"status": "ok" if r.is_success else "error", "http_status": r.status_code, "data": data}


publer = PublerConnector()
