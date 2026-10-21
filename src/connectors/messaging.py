# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""Messaging connector — WhatsApp, Telegram, SMS (Twilio), in-app."""

from __future__ import annotations

import os
from typing import Any, Dict


class MessagingConnector:
    def __init__(self) -> None:
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.whatsapp_from = os.getenv("WHATSAPP_FROM", "")

    def health(self) -> Dict[str, Any]:
        configured = bool(self.twilio_sid or self.telegram_token)
        return {
            "status": "ready" if configured else "unconfigured",
            "capabilities": ("comm.messaging",),
        }

    def send(
        self,
        channel: str,
        to: str,
        body: str,
        *,
        user_confirmed: bool = False,
    ) -> Dict[str, Any]:
        channel = channel.lower().strip()
        if not user_confirmed:
            return {
                "status": "needs_approval",
                "message": "Sending messages requires explicit user confirmation",
                "channel": channel,
                "to": to,
            }
        if channel not in {"sms", "whatsapp", "telegram", "in_app"}:
            return {"status": "error", "message": f"Unsupported channel: {channel}"}
        return {
            "status": "queued",
            "note": f"Wire {channel} provider send",
            "channel": channel,
            "to": to,
            "body_preview": body[:80],
        }
