"""Saphira Autonomous Commerce OS — governance, state, audit, and Stripe integrity.

This package implements the locked implementation contract:
  CommercialAuthorityPolicy → append-only audit → Stripe signature verification
  → state-transition enforcement.

No external communication is enabled by default. Payment activation requires a
verified Stripe webhook event. The LLM never owns financial state.
"""

from .authority import (
    CommercialAction,
    CommercialAuthorityPolicy,
    PolicyDecision,
    PolicyResult,
)
from .audit import AuditRecord, AuditStore
from .states import CommercialState, CommercialStateMachine, InvalidTransition
from .stripe_webhooks import StripeWebhookError, StripeWebhookVerifier, WebhookProcessResult

__all__ = [
    "CommercialAction",
    "CommercialAuthorityPolicy",
    "PolicyDecision",
    "PolicyResult",
    "AuditRecord",
    "AuditStore",
    "CommercialState",
    "CommercialStateMachine",
    "InvalidTransition",
    "StripeWebhookError",
    "StripeWebhookVerifier",
    "WebhookProcessResult",
]
