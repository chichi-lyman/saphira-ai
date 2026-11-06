# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# n8n / Make.com / Zapier webhook bridge (bidirectional)

"""
Outbound triggers + helpers for inbound event handling.

Automation tools (Zapier, Make, n8n) act as bridges that move data between
Saphira and external systems (spreadsheets, CRMs, revenue trackers, etc.).
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import requests

logger = logging.getLogger("SaphiraWebhooks")


class WebhookBridge:
    def __init__(self):
        # Outbound destinations (Saphira → automation tool)
        self.n8n_cross_post = os.getenv(
            "N8N_CROSS_POST_WEBHOOK",
            "https://automation.woodsaistudio.com/webhook/cross-post",
        )
        self.n8n_onboarding = os.getenv(
            "N8N_ONBOARDING_WEBHOOK",
            "https://automation.woodsaistudio.com/webhook/onboarding",
        )
        self.n8n_revenue = os.getenv("N8N_REVENUE_WEBHOOK", "")
        self.make_webhook = os.getenv("MAKE_WEBHOOK_URL", "")
        self.zapier_hook = os.getenv("ZAPIER_WEBHOOK_URL", "")
        self.generic_hooks: List[str] = [
            u.strip()
            for u in os.getenv("SAPHIRA_OUTBOUND_WEBHOOKS", "").split(",")
            if u.strip()
        ]

        # Shared secret for inbound verification (automation → Saphira)
        self.inbound_secret = os.getenv("SAPHIRA_AUTOMATION_WEBHOOK_SECRET", "")

    # ------------------------------------------------------------------
    # Outbound
    # ------------------------------------------------------------------

    def trigger_cross_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post(self.n8n_cross_post, payload, label="n8n_cross_post")

    def trigger_onboarding(self, email: str, tier: str) -> Dict[str, Any]:
        return self._post(
            self.n8n_onboarding,
            {"email": email, "tier": tier, "creator": "Chelsea Megan Woods"},
            label="n8n_onboarding",
        )

    def trigger_make(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.make_webhook:
            return {"status": "skipped", "message": "MAKE_WEBHOOK_URL not set"}
        return self._post(self.make_webhook, payload, label="make")

    def trigger_zapier(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.zapier_hook:
            return {"status": "skipped", "message": "ZAPIER_WEBHOOK_URL not set"}
        return self._post(self.zapier_hook, payload, label="zapier")

    def sync_revenue_event(
        self,
        *,
        event_type: str,
        amount: Optional[float] = None,
        currency: str = "USD",
        source: str = "saphira",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Push a revenue / commerce event toward the automation layer so Zapier/
        Make/n8n can write it into the revenue-engine tracker spreadsheet.
        """
        payload = {
            "event": "revenue_sync",
            "event_type": event_type,
            "amount": amount,
            "currency": currency,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "creator": "Chelsea Megan Woods",
        }
        results = []
        if self.n8n_revenue:
            results.append(self._post(self.n8n_revenue, payload, label="n8n_revenue"))
        if self.zapier_hook:
            results.append(self._post(self.zapier_hook, payload, label="zapier_revenue"))
        if self.make_webhook:
            results.append(self._post(self.make_webhook, payload, label="make_revenue"))
        for url in self.generic_hooks:
            results.append(self._post(url, payload, label="generic"))
        if not results:
            return {"status": "skipped", "message": "no revenue / outbound webhooks configured"}
        # Prefer first success
        for r in results:
            if r.get("status") in ("ok", "success") or r.get("status") not in ("error", "skipped"):
                return {"status": "ok", "results": results}
        return {"status": "error", "results": results}

    def broadcast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fire the same payload to every configured outbound destination."""
        results = {}
        if self.n8n_cross_post:
            results["n8n_cross_post"] = self._post(self.n8n_cross_post, payload, label="n8n")
        if self.make_webhook:
            results["make"] = self._post(self.make_webhook, payload, label="make")
        if self.zapier_hook:
            results["zapier"] = self._post(self.zapier_hook, payload, label="zapier")
        for i, url in enumerate(self.generic_hooks):
            results[f"generic_{i}"] = self._post(url, payload, label=f"generic_{i}")
        return {"status": "ok", "results": results}

    def _post(self, url: str, payload: Dict[str, Any], label: str = "") -> Dict[str, Any]:
        if not url:
            return {"status": "skipped", "message": f"{label or 'webhook'} URL empty"}
        try:
            r = requests.post(url, json=payload, timeout=25)
            r.raise_for_status()
            body: Any
            try:
                body = r.json() if r.content else {"status": "ok"}
            except Exception:
                body = {"status": "ok", "raw": r.text[:200]}
            return {"status": "ok", "label": label, "response": body}
        except Exception as e:
            logger.error("Webhook error (%s %s): %s", label, url, e)
            return {"status": "error", "label": label, "message": str(e)}

    # ------------------------------------------------------------------
    # Inbound helpers (called by FastAPI router)
    # ------------------------------------------------------------------

    def verify_inbound(self, provided_secret: Optional[str]) -> bool:
        if not self.inbound_secret:
            # If no secret configured, allow only in non-production
            env = os.getenv("ENVIRONMENT", os.getenv("SAPHIRA_ENV", "development")).lower()
            return env not in ("production", "prod")
        return bool(provided_secret) and provided_secret == self.inbound_secret

    def handle_inbound_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize an inbound event from Zapier / Make / n8n.

        Expected shapes (flexible):
          { "type": "revenue_update", "amount": 12.5, ... }
          { "event": "sheet_row", "row": {...} }
          { "action": "knowledge_expand", "content": "..." }
        """
        etype = (
            event.get("type")
            or event.get("event")
            or event.get("action")
            or "unknown"
        )
        logger.info("inbound automation event type=%s keys=%s", etype, list(event.keys()))

        # Lightweight routing; extend as new automation scenarios appear
        if etype in ("revenue_update", "revenue_sync", "sheet_row", "tracker_update"):
            return {
                "status": "accepted",
                "handled_as": "revenue_or_tracker",
                "echo": {k: event.get(k) for k in ("amount", "currency", "row", "source") if k in event},
            }
        if etype in ("knowledge_expand", "ingest", "research_result"):
            return {
                "status": "accepted",
                "handled_as": "knowledge",
                "note": "Payload logged for memory / knowledge expansion pipeline",
            }
        return {
            "status": "accepted",
            "handled_as": "generic",
            "type": etype,
        }


# Module-level singleton for convenience
_bridge: Optional[WebhookBridge] = None


def get_webhook_bridge() -> WebhookBridge:
    global _bridge
    if _bridge is None:
        _bridge = WebhookBridge()
    return _bridge
