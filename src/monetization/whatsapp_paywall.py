"""Saphira WhatsApp Freemium Gate.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Defines subscription tiers and a message-limit gate for WhatsApp Cloud API
conversations. This module never sends WhatsApp messages or creates Stripe
charges. It only returns whether the user may continue and an upgrade CTA
when the free allowance is exhausted.

Stripe payment links are read from environment variables so secrets and
live URLs stay out of source control. Wire the actual WhatsApp send path
through the plugin registry + CommercialAuthorityPolicy (REQUIRE_APPROVAL
for outbound messages).
"""
from __future__ import annotations

import os
from typing import Any, Literal

TierName = Literal["FREE", "DANGEROUS", "BADDIE", "CEO"]

# Message limits: FREE is intentionally tight so the upgrade CTA fires early.
# CEO is unlimited (-1). Limits are soft product policy, not hard billing.
TIERS: dict[str, dict[str, Any]] = {
    "FREE": {
        "price": 0,
        "limit": 10,
        "features": ["Basic chat", "Daily 10 messages"],
        "stripe_link_env": None,
    },
    "DANGEROUS": {
        "price": 19,
        "limit": 2000,
        "features": ["Full agent suite", "Memory", "Priority queue"],
        "stripe_link_env": "STRIPE_LINK_DANGEROUS",
    },
    "BADDIE": {
        "price": 49,
        "limit": 10000,
        "features": ["Advanced automation", "Priority support", "API access"],
        "stripe_link_env": "STRIPE_LINK_BADDIE",
    },
    "CEO": {
        "price": 199,
        "limit": -1,  # unlimited
        "features": ["Unlimited", "1:1 onboarding", "Full API", "Priority agents"],
        "stripe_link_env": "STRIPE_LINK_CEO",
    },
}

# Public lead-magnet number (documented; not a secret).
WHATSAPP_LEAD_NUMBER = "18133470699"
WA_ME_BASE = f"https://wa.me/{WHATSAPP_LEAD_NUMBER}"


def get_tier(tier: str | None) -> dict[str, Any]:
    """Return tier definition; defaults to FREE for unknown/empty."""
    key = (tier or "FREE").strip().upper()
    return TIERS.get(key, TIERS["FREE"])


def _stripe_link(tier_key: str) -> str:
    env_name = TIERS[tier_key].get("stripe_link_env")
    if not env_name:
        return ""
    return (os.getenv(env_name) or "").strip()


def upgrade_cta(from_tier: str = "FREE", to_tier: str = "DANGEROUS") -> str:
    """Build a warm upgrade message with Stripe link + WhatsApp deep link."""
    to_key = to_tier.strip().upper()
    if to_key not in TIERS or to_key == "FREE":
        to_key = "DANGEROUS"
    link = _stripe_link(to_key)
    price = TIERS[to_key]["price"]
    label = to_key.title() if to_key != "CEO" else "CEO"
    if link:
        return (
            f"You're so close to CEO energy 🔥 Upgrade to {label} (${price}/mo) "
            f"for more room to build: {link} — or tap to chat: {WA_ME_BASE}"
        )
    return (
        f"You're so close to CEO energy 🔥 Upgrade to {label} (${price}/mo) "
        f"— set STRIPE_LINK_{to_key} in the environment, or tap: {WA_ME_BASE}"
    )


def check_limit(
    user_id: str,
    msg_count: int,
    tier: str = "FREE",
) -> dict[str, Any]:
    """Evaluate whether the user may send another message under their tier.

    Returns a structured result the WhatsApp adapter / plugin can act on:
    - allowed: bool
    - remaining: int | None  (-1 tier limit means unlimited)
    - upgrade_message: str | None  (only when blocked on FREE)
    - tier: normalized tier name

    Does not persist state and does not send messages.
    """
    _ = user_id  # reserved for future usage metering / audit correlation
    tier_key = (tier or "FREE").strip().upper()
    if tier_key not in TIERS:
        tier_key = "FREE"
    definition = TIERS[tier_key]
    limit = int(definition["limit"])

    if limit < 0:
        return {
            "allowed": True,
            "remaining": -1,
            "upgrade_message": None,
            "tier": tier_key,
        }

    remaining = max(0, limit - int(msg_count))
    if remaining > 0:
        return {
            "allowed": True,
            "remaining": remaining,
            "upgrade_message": None,
            "tier": tier_key,
        }

    # Soft gate: only FREE is forced to upgrade CTA at the product limit.
    if tier_key == "FREE":
        return {
            "allowed": False,
            "remaining": 0,
            "upgrade_message": upgrade_cta(from_tier="FREE", to_tier="DANGEROUS"),
            "tier": tier_key,
        }

    # Paid tiers at limit: still allow (ops can raise limit later); surface CTA optionally.
    return {
        "allowed": True,
        "remaining": 0,
        "upgrade_message": upgrade_cta(from_tier=tier_key, to_tier="CEO"),
        "tier": tier_key,
    }
