"""CommercialAuthorityPolicy — governance kernel for consequential commercial actions.

Every commercial action must pass through this policy before execution.
The language model never bypasses this layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class CommercialAction(str, Enum):
    """Catalog of consequential commercial actions."""

    DISCOVER_PROSPECTS = "DISCOVER_PROSPECTS"
    RESEARCH_PUBLIC_BUSINESS = "RESEARCH_PUBLIC_BUSINESS"
    SCORE_PROSPECT = "SCORE_PROSPECT"
    GENERATE_PITCH = "GENERATE_PITCH"
    INITIATE_OUTREACH = "INITIATE_OUTREACH"
    CONDUCT_SALES_CALL = "CONDUCT_SALES_CALL"
    PRESENT_LEADOS_OFFER = "PRESENT_LEADOS_OFFER"
    GENERATE_CHECKOUT = "GENERATE_CHECKOUT"
    CONFIRM_PAYMENT = "CONFIRM_PAYMENT"
    ACTIVATE_SUBSCRIPTION = "ACTIVATE_SUBSCRIPTION"
    ONBOARD_CUSTOMER = "ONBOARD_CUSTOMER"
    DELIVER_SERVICE = "DELIVER_SERVICE"
    SEND_CUSTOMER_SUPPORT = "SEND_CUSTOMER_SUPPORT"
    APPLY_DISCOUNT = "APPLY_DISCOUNT"
    CHANGE_STANDARD_PRICING = "CHANGE_STANDARD_PRICING"
    REFUND_ABOVE_THRESHOLD = "REFUND_ABOVE_THRESHOLD"
    SIGN_NONSTANDARD_AGREEMENT = "SIGN_NONSTANDARD_AGREEMENT"
    MAKE_REGULATED_CLAIM = "MAKE_REGULATED_CLAIM"
    SPEND_COMPANY_MONEY = "SPEND_COMPANY_MONEY"
    UNSUPPORTED_GUARANTEE = "UNSUPPORTED_GUARANTEE"
    USE_UNAPPROVED_CHANNEL = "USE_UNAPPROVED_CHANNEL"


_DEFAULT_MATRIX: dict[CommercialAction, PolicyDecision] = {
    CommercialAction.DISCOVER_PROSPECTS: PolicyDecision.ALLOW,
    CommercialAction.RESEARCH_PUBLIC_BUSINESS: PolicyDecision.ALLOW,
    CommercialAction.SCORE_PROSPECT: PolicyDecision.ALLOW,
    CommercialAction.GENERATE_PITCH: PolicyDecision.ALLOW,
    CommercialAction.INITIATE_OUTREACH: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.CONDUCT_SALES_CALL: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.PRESENT_LEADOS_OFFER: PolicyDecision.ALLOW,
    CommercialAction.GENERATE_CHECKOUT: PolicyDecision.ALLOW,
    CommercialAction.CONFIRM_PAYMENT: PolicyDecision.DENY,
    CommercialAction.ACTIVATE_SUBSCRIPTION: PolicyDecision.DENY,
    CommercialAction.ONBOARD_CUSTOMER: PolicyDecision.ALLOW,
    CommercialAction.DELIVER_SERVICE: PolicyDecision.ALLOW,
    CommercialAction.SEND_CUSTOMER_SUPPORT: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.APPLY_DISCOUNT: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.CHANGE_STANDARD_PRICING: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.REFUND_ABOVE_THRESHOLD: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.SIGN_NONSTANDARD_AGREEMENT: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.MAKE_REGULATED_CLAIM: PolicyDecision.DENY,
    CommercialAction.SPEND_COMPANY_MONEY: PolicyDecision.REQUIRE_APPROVAL,
    CommercialAction.UNSUPPORTED_GUARANTEE: PolicyDecision.DENY,
    CommercialAction.USE_UNAPPROVED_CHANNEL: PolicyDecision.DENY,
}

LEADOS_MONTHLY_PRICE_USD = 500
REFUND_APPROVAL_THRESHOLD_USD = 50


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    action: CommercialAction
    reason: str
    context: dict[str, Any]

    @property
    def may_execute(self) -> bool:
        return self.decision is PolicyDecision.ALLOW


class CommercialAuthorityPolicy:
    """Machine-readable commercial authority matrix.

    Governance happens before execution. DENY and REQUIRE_APPROVAL never execute.
    """

    def __init__(
        self,
        matrix: dict[CommercialAction, PolicyDecision] | None = None,
        *,
        leados_price_usd: int = LEADOS_MONTHLY_PRICE_USD,
        refund_threshold_usd: float = REFUND_APPROVAL_THRESHOLD_USD,
    ) -> None:
        self._matrix = dict(matrix or _DEFAULT_MATRIX)
        self.leados_price_usd = leados_price_usd
        self.refund_threshold_usd = refund_threshold_usd

    def authorize(
        self,
        action: CommercialAction | str,
        *,
        context: dict[str, Any] | None = None,
    ) -> PolicyResult:
        context = dict(context or {})
        if isinstance(action, str):
            try:
                action = CommercialAction(action)
            except ValueError:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    action=CommercialAction.MAKE_REGULATED_CLAIM,
                    reason=f"Unknown commercial action: {action}",
                    context=context,
                )

        if action in (CommercialAction.CONFIRM_PAYMENT, CommercialAction.ACTIVATE_SUBSCRIPTION):
            if context.get("stripe_verified") is True and context.get("stripe_event_id"):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    action=action,
                    reason="Verified Stripe event permits payment confirmation / activation",
                    context=context,
                )
            return PolicyResult(
                decision=PolicyDecision.DENY,
                action=action,
                reason="Payment confirmation requires a verified Stripe webhook event",
                context=context,
            )

        if action is CommercialAction.PRESENT_LEADOS_OFFER:
            offered = context.get("price_usd")
            if offered is not None and int(offered) != self.leados_price_usd:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    action=action,
                    reason=f"Out-of-policy price {offered}; standard LeadOS is ${self.leados_price_usd}/mo",
                    context=context,
                )

        if action is CommercialAction.APPLY_DISCOUNT:
            amount = float(context.get("discount_usd") or 0)
            if amount > 0:
                return PolicyResult(
                    decision=PolicyDecision.REQUIRE_APPROVAL,
                    action=action,
                    reason=f"Discount of ${amount} requires human approval",
                    context=context,
                )

        if action is CommercialAction.REFUND_ABOVE_THRESHOLD:
            amount = float(context.get("refund_usd") or 0)
            if amount >= self.refund_threshold_usd:
                return PolicyResult(
                    decision=PolicyDecision.REQUIRE_APPROVAL,
                    action=action,
                    reason=f"Refund ${amount} exceeds threshold ${self.refund_threshold_usd}",
                    context=context,
                )
            if amount > 0:
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    action=action,
                    reason=f"Refund ${amount} within threshold",
                    context=context,
                )

        decision = self._matrix.get(action, PolicyDecision.DENY)
        reasons = {
            PolicyDecision.ALLOW: "Action permitted by commercial authority matrix",
            PolicyDecision.REQUIRE_APPROVAL: "Action requires human approval per commercial policy",
            PolicyDecision.DENY: "Action denied by commercial authority matrix",
        }
        return PolicyResult(
            decision=decision,
            action=action,
            reason=reasons[decision],
            context=context,
        )
