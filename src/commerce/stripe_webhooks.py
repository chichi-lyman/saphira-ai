"""Stripe webhook signature verification and idempotent event processing.

Critical rules:
  - Never trust client-supplied payment status.
  - Only a signature-verified Stripe event may drive PAYMENT_PENDING → CUSTOMER.
  - Duplicate event IDs are ignored (idempotent).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable

import stripe

from .audit import AuditStore
from .authority import CommercialAction, CommercialAuthorityPolicy, PolicyDecision
from .states import CommercialState, CommercialStateMachine, InvalidTransition


class StripeWebhookError(Exception):
    """Raised when a webhook cannot be accepted."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        self.status_code = status_code
        super().__init__(message)


@dataclass
class WebhookProcessResult:
    accepted: bool
    event_id: str
    event_type: str
    state_transition: str | None = None
    reason: str = ""
    audit_ids: list[str] = field(default_factory=list)


_ACTIVATION_EVENTS = frozenset({
    "checkout.session.completed",
    "invoice.paid",
    "customer.subscription.created",
})


class StripeWebhookVerifier:
    """Verify Stripe signatures and apply verified events to the commercial state machine."""

    def __init__(
        self,
        *,
        webhook_secret: str | None = None,
        policy: CommercialAuthorityPolicy | None = None,
        audit: AuditStore | None = None,
        state_machines: dict[str, CommercialStateMachine] | None = None,
    ) -> None:
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.policy = policy or CommercialAuthorityPolicy()
        self.audit = audit or AuditStore()
        self._machines = state_machines if state_machines is not None else {}
        self._processed_event_ids: set[str] = set()

    def construct_event(
        self,
        payload: bytes | str,
        sig_header: str | None,
    ) -> stripe.Event:
        """Verify signature and return a Stripe Event. Raises StripeWebhookError on failure."""
        if not self.webhook_secret:
            raise StripeWebhookError("STRIPE_WEBHOOK_SECRET is not configured", status_code=500)
        if not sig_header:
            raise StripeWebhookError("Missing Stripe-Signature header", status_code=401)

        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        try:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=sig_header,
                secret=self.webhook_secret,
            )
        except ValueError as exc:
            raise StripeWebhookError(f"Malformed payload: {exc}", status_code=400) from exc
        except stripe.error.SignatureVerificationError as exc:
            raise StripeWebhookError(f"Invalid signature: {exc}", status_code=401) from exc

        return event

    def process_verified_event(
        self,
        event: stripe.Event | dict[str, Any],
        *,
        target_id: str,
        actor: str = "stripe_webhook",
    ) -> WebhookProcessResult:
        """Apply a already verified event. Does not re-check signature.

        Idempotent on event ID. Only activation-class events may move
        PAYMENT_PENDING → CUSTOMER, and only through the policy gate.
        """
        if hasattr(event, "to_dict"):
            data = event.to_dict()
        else:
            data = dict(event)

        event_id = str(data.get("id") or "")
        event_type = str(data.get("type") or "")

        if not event_id:
            raise StripeWebhookError("Event missing id", status_code=400)

        if event_id in self._processed_event_ids:
            rec = self.audit.append(
                actor=actor,
                action="STRIPE_EVENT_DUPLICATE",
                target_type="customer",
                target_id=target_id,
                policy_decision=PolicyDecision.DENY.value,
                reason="Duplicate Stripe event ignored (idempotent)",
                event_id=event_id,
                executed=False,
                metadata={"event_type": event_type},
            )
            return WebhookProcessResult(
                accepted=False,
                event_id=event_id,
                event_type=event_type,
                reason="Duplicate event ignored",
                audit_ids=[rec.audit_id],
            )

        if event_type not in _ACTIVATION_EVENTS:
            rec = self.audit.append(
                actor=actor,
                action="STRIPE_EVENT_IGNORED",
                target_type="customer",
                target_id=target_id,
                policy_decision=PolicyDecision.DENY.value,
                reason=f"Event type {event_type} is not an activation event",
                event_id=event_id,
                executed=False,
                metadata={"event_type": event_type},
            )
            return WebhookProcessResult(
                accepted=False,
                event_id=event_id,
                event_type=event_type,
                reason=f"Non-activation event type: {event_type}",
                audit_ids=[rec.audit_id],
            )

        machine = self._machines.get(target_id)
        if machine is None:
            machine = CommercialStateMachine(initial=CommercialState.PAYMENT_PENDING)
            self._machines[target_id] = machine

        policy_result = self.policy.authorize(
            CommercialAction.ACTIVATE_SUBSCRIPTION,
            context={"stripe_verified": True, "stripe_event_id": event_id, "target_id": target_id},
        )
        decision_rec = self.audit.append(
            actor=actor,
            action=CommercialAction.ACTIVATE_SUBSCRIPTION.value,
            target_type="customer",
            target_id=target_id,
            policy_decision=policy_result.decision.value,
            reason=policy_result.reason,
            previous_state=machine.state.value,
            event_id=event_id,
            executed=False,
            metadata={"event_type": event_type},
        )

        if not policy_result.may_execute:
            return WebhookProcessResult(
                accepted=False,
                event_id=event_id,
                event_type=event_type,
                reason=policy_result.reason,
                audit_ids=[decision_rec.audit_id],
            )

        try:
            transition = machine.transition(
                CommercialState.CUSTOMER,
                stripe_verified=True,
            )
        except InvalidTransition as exc:
            fail_rec = self.audit.append(
                actor=actor,
                action=CommercialAction.ACTIVATE_SUBSCRIPTION.value,
                target_type="customer",
                target_id=target_id,
                policy_decision=PolicyDecision.DENY.value,
                reason=str(exc),
                previous_state=machine.state.value,
                event_id=event_id,
                executed=False,
                metadata={"event_type": event_type},
            )
            return WebhookProcessResult(
                accepted=False,
                event_id=event_id,
                event_type=event_type,
                reason=str(exc),
                audit_ids=[decision_rec.audit_id, fail_rec.audit_id],
            )

        self._processed_event_ids.add(event_id)
        exec_rec = self.audit.append(
            actor=actor,
            action=CommercialAction.ACTIVATE_SUBSCRIPTION.value,
            target_type="customer",
            target_id=target_id,
            policy_decision=PolicyDecision.ALLOW.value,
            reason="Verified Stripe event activated customer",
            previous_state=transition.previous.value,
            resulting_state=transition.resulting.value,
            event_id=event_id,
            executed=True,
            metadata={"event_type": event_type},
        )
        return WebhookProcessResult(
            accepted=True,
            event_id=event_id,
            event_type=event_type,
            state_transition=f"{transition.previous.value}→{transition.resulting.value}",
            reason="Customer activated from verified Stripe event",
            audit_ids=[decision_rec.audit_id, exec_rec.audit_id],
        )

    def handle_http_webhook(
        self,
        payload: bytes | str,
        sig_header: str | None,
        *,
        target_id_resolver: Callable[[dict[str, Any]], str],
        actor: str = "stripe_webhook",
    ) -> WebhookProcessResult:
        """Full path: verify signature → resolve target → process event."""
        event = self.construct_event(payload, sig_header)
        data = event.to_dict() if hasattr(event, "to_dict") else dict(event)
        target_id = target_id_resolver(data)
        return self.process_verified_event(event, target_id=target_id, actor=actor)
