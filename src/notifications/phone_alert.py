"""Optional phone alert transport for successful paid activations."""
from __future__ import annotations

import os
import logging
import httpx

logger = logging.getLogger("saphira.notifications.phone")


async def send_purchase_alert(*, email: str, event_id: str, amount: int | None = None) -> bool:
    """Send a Telegram alert when configured; otherwise no-op safely."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return False

    amount_text = f"${amount / 100:.2f}" if amount is not None else "amount unavailable"
    text = f"💰 Saphira sale\nCustomer: {email}\nAmount: {amount_text}\nEvent: {event_id}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": text})
        if 200 <= response.status_code < 300:
            return True
        logger.error("Phone alert failed: %s %s", response.status_code, response.text)
        return False
    except httpx.HTTPError:
        logger.exception("Phone alert transport failed")
        return False
