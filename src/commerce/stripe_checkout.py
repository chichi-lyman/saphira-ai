"""Stripe subscription checkout endpoint for Saphira AI."""
from __future__ import annotations

import os

import stripe
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/v1/checkout", tags=["Commerce Platform"])


@router.post("/create-session")
async def create_subscription_checkout_session():
    secret = os.getenv("STRIPE_SECRET_KEY")
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe checkout is not configured")

    stripe.api_key = secret
    domain = os.getenv("PRODUCTION_DOMAIN_URL", "http://localhost:3000").rstrip("/")
    price_id = os.getenv("STRIPE_PRICE_ID")

    try:
        if price_id:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=f"{domain}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain}/",
            )
        else:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Saphira AI — Client Acquisition",
                            "description": "AI-assisted local lead generation and governed outreach workflow.",
                        },
                        "unit_amount": 19900,
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }],
                success_url=f"{domain}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain}/",
            )
        return RedirectResponse(url=session.url, status_code=303)
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail="Stripe checkout could not be created") from exc
