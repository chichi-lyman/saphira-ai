"""Commercial lifecycle state machine with validated transitions.

Invalid transitions are rejected. PAYMENT_PENDING → CUSTOMER is allowed only
when the caller supplies stripe_verified=True (from a verified webhook).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class CommercialState(str, Enum):
    PROSPECT = "PROSPECT"
    QUALIFIED = "QUALIFIED"
    CONTACTED = "CONTACTED"
    ENGAGED = "ENGAGED"
    SALES_CONVERSATION = "SALES_CONVERSATION"
    OFFER_PRESENTED = "OFFER_PRESENTED"
    CHECKOUT_CREATED = "CHECKOUT_CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CUSTOMER = "CUSTOMER"
    ONBOARDING = "ONBOARDING"
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    CANCELLED = "CANCELLED"


_ALLOWED: dict[CommercialState, frozenset[CommercialState]] = {
    CommercialState.PROSPECT: frozenset({CommercialState.QUALIFIED, CommercialState.CANCELLED}),
    CommercialState.QUALIFIED: frozenset({CommercialState.CONTACTED, CommercialState.CANCELLED}),
    CommercialState.CONTACTED: frozenset({CommercialState.ENGAGED, CommercialState.CANCELLED}),
    CommercialState.ENGAGED: frozenset({CommercialState.SALES_CONVERSATION, CommercialState.CANCELLED}),
    CommercialState.SALES_CONVERSATION: frozenset({
        CommercialState.OFFER_PRESENTED, CommercialState.ENGAGED, CommercialState.CANCELLED
    }),
    CommercialState.OFFER_PRESENTED: frozenset({
        CommercialState.CHECKOUT_CREATED, CommercialState.SALES_CONVERSATION, CommercialState.CANCELLED
    }),
    CommercialState.CHECKOUT_CREATED: frozenset({
        CommercialState.PAYMENT_PENDING, CommercialState.CANCELLED
    }),
    CommercialState.PAYMENT_PENDING: frozenset({
        CommercialState.CUSTOMER, CommercialState.CANCELLED
    }),
    CommercialState.CUSTOMER: frozenset({CommercialState.ONBOARDING, CommercialState.CANCELLED}),
    CommercialState.ONBOARDING: frozenset({CommercialState.ACTIVE, CommercialState.CANCELLED}),
    CommercialState.ACTIVE: frozenset({CommercialState.AT_RISK, CommercialState.CANCELLED}),
    CommercialState.AT_RISK: frozenset({CommercialState.ACTIVE, CommercialState.CANCELLED}),
    CommercialState.CANCELLED: frozenset(),
}


class InvalidTransition(Exception):
    def __init__(self, source: CommercialState, target: CommercialState, reason: str) -> None:
        self.source = source
        self.target = target
        self.reason = reason
        super().__init__(f"Invalid transition {source.value} → {target.value}: {reason}")


@dataclass
class TransitionResult:
    previous: CommercialState
    resulting: CommercialState
    accepted: bool
    reason: str


class CommercialStateMachine:
    """Validates and records commercial state transitions."""

    def __init__(self, initial: CommercialState = CommercialState.PROSPECT) -> None:
        self._state = initial

    @property
    def state(self) -> CommercialState:
        return self._state

    def can_transition(
        self,
        target: CommercialState,
        *,
        stripe_verified: bool = False,
    ) -> tuple[bool, str]:
        allowed = _ALLOWED.get(self._state, frozenset())
        if target not in allowed:
            return False, f"{self._state.value} → {target.value} is not in the allowed transition set"

        if (
            self._state is CommercialState.PAYMENT_PENDING
            and target is CommercialState.CUSTOMER
            and not stripe_verified
        ):
            return False, "PAYMENT_PENDING → CUSTOMER requires a verified Stripe event"

        return True, "Transition permitted"

    def transition(
        self,
        target: CommercialState,
        *,
        stripe_verified: bool = False,
    ) -> TransitionResult:
        ok, reason = self.can_transition(target, stripe_verified=stripe_verified)
        if not ok:
            raise InvalidTransition(self._state, target, reason)
        previous = self._state
        self._state = target
        return TransitionResult(
            previous=previous,
            resulting=target,
            accepted=True,
            reason=reason,
        )

    @staticmethod
    def is_valid_path(states: Iterable[CommercialState], *, final_stripe_verified: bool = False) -> bool:
        seq = list(states)
        if not seq:
            return True
        sm = CommercialStateMachine(initial=seq[0])
        for nxt in seq[1:]:
            stripe = (
                sm.state is CommercialState.PAYMENT_PENDING
                and nxt is CommercialState.CUSTOMER
                and final_stripe_verified
            )
            ok, _ = sm.can_transition(nxt, stripe_verified=stripe)
            if not ok:
                return False
            sm.transition(nxt, stripe_verified=stripe)
        return True
