"""Transactional onboarding email delivery for paid Saphira activations."""
from __future__ import annotations

import os
import logging
import httpx

logger = logging.getLogger("saphira.notifications")
RESEND_URL = "https://api.resend.com/emails"


async def send_client_welcome_email(
    recipient_email: str,
    *,
    event_id: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    from_address = os.getenv("RESEND_FROM", "Saphira AI <onboarding@resend.dev>")
    dashboard_url = os.getenv("PRODUCTION_DOMAIN_URL", "http://localhost:3000").rstrip("/") + "/dashboard"

    if not api_key or not recipient_email:
        logger.warning("Welcome email skipped: missing RESEND_API_KEY or recipient")
        return False

    key = f"saphira-welcome/{event_id or recipient_email}"
    payload = {
        "from": from_address,
        "to": [recipient_email],
        "subject": "Saphira AI is activated",
        "html": f"""
        <div style=\"font-family:Inter,Arial,sans-serif;max-width:600px;margin:auto;padding:32px;color:#172033\">
          <h1 style=\"margin-bottom:8px\">Saphira AI is activated.</h1>
          <p>Your subscription was verified and your workspace is ready for onboarding.</p>
          <p>Next: connect your business goals, calendar, CRM, and lead sources.</p>
          <p><a href=\"{dashboard_url}\" style=\"display:inline-block;padding:12px 20px;border-radius:10px;background:#111;color:#fff;text-decoration:none\">Open Saphira Workspace</a></p>
          <p style=\"font-size:12px;color:#667085\">Tenant: {tenant_id or 'pending'} · Event: {event_id or 'n/a'}</p>
        </div>
        """,
        "text": f"Saphira AI is activated. Open your workspace: {dashboard_url}",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Saphira-AI/production",
        "Idempotency-Key": key,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(RESEND_URL, json=payload, headers=headers)
        if 200 <= response.status_code < 300:
            logger.info("Welcome email accepted for %s", recipient_email)
            return True
        logger.error("Resend rejected welcome email: %s %s", response.status_code, response.text)
        return False
    except httpx.HTTPError:
        logger.exception("Resend request failed")
        return False
