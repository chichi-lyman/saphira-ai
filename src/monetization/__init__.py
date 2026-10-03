"""Saphira monetization helpers — freemium gates and tier definitions.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

These modules define product tiers and gate logic only. They do not
send messages, charge cards, or activate subscriptions. External
communication and payment activation remain under CommercialAuthorityPolicy
and verified Stripe webhooks.
"""

from .whatsapp_paywall import (
    TIERS,
    TierName,
    check_limit,
    get_tier,
    upgrade_cta,
)

__all__ = [
    "TIERS",
    "TierName",
    "check_limit",
    "get_tier",
    "upgrade_cta",
]
