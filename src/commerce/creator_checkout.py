"""One-time and subscription checkout for creator products.

Uses Stripe Checkout Sessions only — never trusts client-side payment status.
Activation still flows through signature-verified webhooks + CommercialAuthorityPolicy.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.commerce.authority import CommercialAction, CommercialAuthorityPolicy, PolicyDecision
from src.commerce.products import get_product, list_products

logger = logging.getLogger("saphira.creator_checkout")
router = APIRouter(prefix="/api/v1/creator", tags=["Creator Commerce"])
_policy = CommercialAuthorityPolicy()


class CheckoutRequest(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    quantity: int = Field(default=1, ge=1, le=20)
    customer_email: str | None = Field(default=None, max_length=320)
    success_path: str = Field(default="/success.html", max_length=200)
    cancel_path: str = Field(default="/", max_length=200)


def _stripe_ready() -> str:
    secret = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe is not configured (STRIPE_SECRET_KEY)")
    return secret


@router.get("/products")
async def creator_products() -> dict[str, Any]:
    return {"products": list_products()}


@router.post("/checkout")
async def create_creator_checkout(body: CheckoutRequest) -> dict[str, Any]:
    decision = _policy.decide(CommercialAction.GENERATE_CHECKOUT)
    if decision.decision == PolicyDecision.DENY:
        raise HTTPException(status_code=403, detail="Checkout denied by commercial policy")

    product = get_product(body.sku)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Unknown product sku: {body.sku}")

    secret = _stripe_ready()
    stripe.api_key = secret
    domain = os.getenv("PRODUCTION_DOMAIN_URL", "http://localhost:3000").rstrip("/")
    success = body.success_path if body.success_path.startswith("/") else f"/{body.success_path}"
    cancel = body.cancel_path if body.cancel_path.startswith("/") else f"/{body.cancel_path}"

    line_item: dict[str, Any]
    price_env = product.stripe_price_id_env
    price_id = os.getenv(price_env, "").strip() if price_env else ""
    if price_id:
        line_item = {"price": price_id, "quantity": body.quantity}
    else:
        price_data: dict[str, Any] = {
            "currency": product.currency,
            "product_data": {"name": product.name, "description": product.description},
            "unit_amount": product.amount_cents,
        }
        if product.mode == "subscription":
            price_data["recurring"] = {"interval": "month"}
        line_item = {"price_data": price_data, "quantity": body.quantity}

    params: dict[str, Any] = {
        "mode": product.mode,
        "line_items": [line_item],
        "success_url": f"{domain}{success}?session_id={{CHECKOUT_SESSION_ID}}&sku={product.sku}",
        "cancel_url": f"{domain}{cancel}",
        "metadata": {
            "sku": product.sku,
            "fulfillment": product.fulfillment,
            "source": "saphira_creator_wedge",
        },
    }
    if body.customer_email:
        params["customer_email"] = body.customer_email.strip().lower()

    try:
        session = stripe.checkout.Session.create(**params)
    except stripe.error.StripeError as exc:
        logger.exception("Stripe checkout failed for sku=%s", product.sku)
        raise HTTPException(status_code=502, detail="Stripe checkout could not be created") from exc

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "sku": product.sku,
        "mode": product.mode,
        "policy": decision.decision.value,
    }
