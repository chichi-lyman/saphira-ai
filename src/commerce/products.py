"""Creator product catalog for the Saphira commerce wedge.

Dogfoods Chelsea Megan Woods products first (book, courses, beauty line).
Prices are cents USD. Stripe Price IDs override inline price_data when set.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    description: str
    amount_cents: int
    currency: str = "usd"
    mode: str = "payment"  # payment | subscription
    stripe_price_id_env: str | None = None
    fulfillment: str = "digital"  # digital | blanka | manual

    def public_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "amount_cents": self.amount_cents,
            "amount_display": f"${self.amount_cents / 100:.2f}",
            "currency": self.currency,
            "mode": self.mode,
            "fulfillment": self.fulfillment,
        }


# Dogfood catalog — expand via env or DB later; keep code as source of truth for Phase 0/1
PRODUCTS: dict[str, Product] = {
    "blueprint-book": Product(
        sku="blueprint-book",
        name="Creator Platform Build Blueprint",
        description="Full blueprint for building a creator platform — money first, community second, discovery third.",
        amount_cents=4700,
        fulfillment="digital",
        stripe_price_id_env="STRIPE_PRICE_BLUEPRINT_BOOK",
    ),
    "saphira-studio-month": Product(
        sku="saphira-studio-month",
        name="Saphira Creator Studio (monthly)",
        description="AI creator studio access — captions, scheduling assist, governed outreach tools.",
        amount_cents=19900,
        mode="subscription",
        fulfillment="digital",
        stripe_price_id_env="STRIPE_PRICE_ID",
    ),
    "makeup-starter": Product(
        sku="makeup-starter",
        name="Chelsea Beauty — Starter Kit",
        description="Starter makeup kit fulfilled via Blanka (or configured fulfillment partner).",
        amount_cents=4900,
        fulfillment="blanka",
        stripe_price_id_env="STRIPE_PRICE_MAKEUP_STARTER",
    ),
    "course-ai-creators": Product(
        sku="course-ai-creators",
        name="AI for Creators — Mini Course",
        description="Short practical course on using Saphira-style agents for content and sales.",
        amount_cents=9700,
        fulfillment="digital",
        stripe_price_id_env="STRIPE_PRICE_COURSE_AI",
    ),
}


def get_product(sku: str) -> Product | None:
    return PRODUCTS.get(sku.strip().lower())


def list_products() -> list[dict[str, Any]]:
    return [p.public_dict() for p in PRODUCTS.values()]
