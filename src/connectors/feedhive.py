# Copyright © 2026 Chelsea Megan Woods
"""FeedHive connector — trigger URL based scheduling.

Docs: https://docs.feedhive.com/workflows/how-to-trigger
Auth: per-workspace trigger URL stored as FEEDHIVE_TRIGGER_URL secret.
"""

from __future__ import annotations

import os
from typing import Any, Optional
import httpx
import logging

logger = logging.getLogger("Saphira.FeedHive")


class FeedHiveConnector:
    name = "feedhive"

    def __init__(self, trigger_url: Optional[str] = None):
        self.trigger_url = trigger_url or os.getenv("FEEDHIVE_TRIGGER_URL", "")

    def configured(self) -> bool:
        return bool(self.trigger_url) and self.trigger_url.startswith("http")

    async def schedule_post(
        self,
        *,
        text: str,
        scheduled: str | None = None,
        media_urls: list[str] | None = None,
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set FEEDHIVE_TRIGGER_URL secret (from FeedHive workflow trigger)",
                "payload_preview": {"text": text[:200], "scheduled": scheduled},
            }

        body: dict[str, Any] = {"text": text}
        if scheduled:
            body["scheduled"] = scheduled
        if media_urls:
            body["media_urls"] = media_urls

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(self.trigger_url, json=body)
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text[:500]}
            return {"status": "ok" if r.is_success else "error", "http_status": r.status_code, "data": data}


feedhive = FeedHiveConnector()
