"""HTTP adapter for the governed Stripe commerce state machine."""
from __future__ import annotations

import os
import uuid
import logging
from typing import Any

import asyncpg
from fastapi import APIRouter, Header, HTTPException, Request

from src.commerce.stripe_webhooks import StripeWebhookError, StripeWebhookVerifier
from src.notifications.phone_alert import send_purchase_alert
from src.notifications.welcome_email import send_client_welcome_email

logger = logging.getLogger("saphira.billing")
router = APIRouter(prefix="/api/v1/billing", tags=["Commerce Automation"])
_verifier = StripeWebhookVerifier()


def _database_dsn() -> str | None:
    value = os.getenv("DATABASE_URL")
    if not value:
        return None
    return value.replace("postgresql+asyncpg://", "postgresql://", 1)


async def _provision_subscription(session: dict[str, Any]) -> tuple[str, bool]:
    """Persist a tenant/subscription using the verified Stripe customer identity."""
    dsn = _database_dsn()
    customer_id = str(session.get("customer") or "")
    subscription_id = str(session.get("subscription") or "")
    details = session.get("customer_details") or {}
    email = str(details.get("email") or "").strip().lower()
    if not customer_id or not email:
        raise HTTPException(status_code=422, detail="Verified Stripe event lacks customer identity")

    tenant_id = f"tenant_{uuid.uuid5(uuid.NAMESPACE_URL, 'saphira:' + customer_id).hex[:24]}"
    if not dsn:
        logger.warning("DATABASE_URL is not configured; webhook accepted without persistence")
        return tenant_id, False

    conn = await asyncpg.connect(dsn)
    try:
        async with conn.transaction():
            inserted = await conn.fetchval(
                """INSERT INTO stripe_processed_events(event_id, event_type) VALUES($1,$2)
                   ON CONFLICT(event_id) DO NOTHING RETURNING event_id""",
                str(session.get("_event_id") or ""),
                "checkout.session.completed",
            )
            if not inserted:
                return tenant_id, False

            await conn.execute(
                """INSERT INTO system_tenants(tenant_id, owner_name, company_name)
                   VALUES($1,$2,$3) ON CONFLICT(tenant_id) DO NOTHING""",
                tenant_id,
                email,
                None,
            )
            await conn.execute(
                """INSERT INTO tenant_subscriptions(
                    subscription_id, tenant_id, customer_email, stripe_customer_id,
                    account_status, current_period_end
                ) VALUES($1,$2,$3,$4,'ACTIVE',NOW())
                ON CONFLICT(subscription_id) DO UPDATE SET account_status='ACTIVE'""",
                subscription_id or f"session_{session.get('id')}",
                tenant_id,
                email,
                customer_id,
            )
        return tenant_id, True
    finally:
        await conn.close()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None, alias="Stripe-Signature")):
    payload = await request.body()
    try:
        event = _verifier.construct_event(payload, stripe_signature)
    except StripeWebhookError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    data = event.to_dict() if hasattr(event, "to_dict") else dict(event)
    event_id = str(data.get("id") or "")
    event_type = str(data.get("type") or "")
    obj = ((data.get("data") or {}).get("object") or {})
    customer_id = str(obj.get("customer") or obj.get("customer_details", {}).get("email") or event_id)

    result = _verifier.process_verified_event(data, target_id=customer_id)
    if not result.accepted:
        return {"status": "ignored", "event_id": event_id, "reason": result.reason}

    obj["_event_id"] = event_id
    tenant_id, persisted = await _provision_subscription(obj)
    email = str((obj.get("customer_details") or {}).get("email") or "")
    amount = obj.get("amount_total")

    if email:
        await send_client_welcome_email(email, event_id=event_id, tenant_id=tenant_id)
        await send_purchase_alert(email=email, event_id=event_id, amount=amount)

    return {
        "status": "processed",
        "event_id": event_id,
        "event_type": event_type,
        "tenant_id": tenant_id,
        "persisted": persisted,
        "state_transition": result.state_transition,
    }
