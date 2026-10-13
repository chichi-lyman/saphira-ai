"""Stripe Checkout and webhook verification helpers.

The module is intentionally not mounted as a public API route automatically.
Callers must enforce user authentication, plan authorization, rate limits, and
audit logging before creating checkout sessions. Never return secret values.
"""
from __future__ import annotations

import os
from typing import Any


class StripeConfigurationError(RuntimeError):
    """Raised when required Stripe configuration is missing."""


def _stripe_module():
    try:
        import stripe
    except ImportError as exc:  # pragma: no cover - depends on install extras
        raise StripeConfigurationError("Install the runtime dependency 'stripe'.") from exc
    return stripe


def create_subscription_checkout(
    *,
    customer_email: str,
    success_url: str,
    cancel_url: str,
    user_id: str,
    idempotency_key: str,
    price_id: str | None = None,
) -> dict[str, str]:
    """Create a subscription Checkout Session; caller must authorize and audit first."""
    secret = os.getenv("STRIPE_SECRET_KEY", "").strip()
    selected_price = (price_id or os.getenv("STRIPE_PRICE_MONTHLY") or os.getenv("STRIPE_PRICE_ID") or "").strip()
    if not secret:
        raise StripeConfigurationError("STRIPE_SECRET_KEY is not configured.")
    if not selected_price:
        raise StripeConfigurationError("Set STRIPE_PRICE_MONTHLY or STRIPE_PRICE_ID.")
    if not customer_email.strip() or not user_id.strip() or not idempotency_key.strip():
        raise ValueError("customer_email, user_id, and idempotency_key are required.")
    if not success_url.startswith("https://") and not success_url.startswith("http://localhost"):
        raise ValueError("success_url must use HTTPS (localhost is allowed for development).")
    if not cancel_url.startswith("https://") and not cancel_url.startswith("http://localhost"):
        raise ValueError("cancel_url must use HTTPS (localhost is allowed for development).")

    stripe = _stripe_module()
    stripe.api_key = secret
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=customer_email.strip(),
        line_items=[{"price": selected_price, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=user_id.strip(),
        metadata={"saphira_user_id": user_id.strip()},
        subscription_data={"metadata": {"saphira_user_id": user_id.strip()}},
        options={"idempotency_key": idempotency_key.strip()},
    )
    return {"id": str(session.id), "url": str(session.url)}


def verify_webhook(payload: bytes, signature: str) -> Any:
    """Verify Stripe's signed raw webhook payload before processing an event."""
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise StripeConfigurationError("STRIPE_WEBHOOK_SECRET is not configured.")
    if not signature:
        raise ValueError("Stripe-Signature header is required.")
    stripe = _stripe_module()
    return stripe.Webhook.construct_event(payload, signature, secret)
