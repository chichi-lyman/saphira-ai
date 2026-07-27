# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# n8n / Make.com webhook bridge

import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("SaphiraWebhooks")

class WebhookBridge:
    def __init__(self):
        self.n8n_cross_post = os.getenv("N8N_CROSS_POST_WEBHOOK", "https://automation.woodsaistudio.com/webhook/cross-post")
        self.n8n_onboarding = os.getenv("N8N_ONBOARDING_WEBHOOK", "https://automation.woodsaistudio.com/webhook/onboarding")
        self.make_webhook = os.getenv("MAKE_WEBHOOK_URL", "")

    def trigger_cross_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post(self.n8n_cross_post, payload)

    def trigger_onboarding(self, email: str, tier: str) -> Dict[str, Any]:
        return self._post(self.n8n_onboarding, {"email": email, "tier": tier, "creator": "Chelsea Megan Woods"})

    def trigger_make(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.make_webhook:
            return {"status": "skipped", "message": "MAKE_WEBHOOK_URL not set"}
        return self._post(self.make_webhook, payload)

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = requests.post(url, json=payload, timeout=25)
            r.raise_for_status()
            return r.json() if r.content else {"status": "ok"}
        except Exception as e:
            logger.error(f"Webhook error ({url}): {e}")
            return {"status": "error", "message": str(e)}
