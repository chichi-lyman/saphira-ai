"""Tests for CommercialAuthorityPolicy, audit chain, state machine, and Stripe verification.

These are the required test gates before any autonomous external communication.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from src.commerce.authority import (
    CommercialAction,
    CommercialAuthorityPolicy,
    PolicyDecision,
)
from src.commerce.audit import AuditStore
from src.commerce.states import (
    CommercialState,
    CommercialStateMachine,
    InvalidTransition,
)
from src.commerce.stripe_webhooks import (
    StripeWebhookError,
    StripeWebhookVerifier,
)


class TestCommercialAuthorityPolicy:
    def setup_method(self) -> None:
        self.policy = CommercialAuthorityPolicy()

    def test_allow_discovery(self) -> None:
        r = self.policy.authorize(CommercialAction.DISCOVER_PROSPECTS)
        assert r.decision is PolicyDecision.ALLOW
        assert r.may_execute is True

    def test_require_approval_outreach(self) -> None:
        r = self.policy.authorize(CommercialAction.INITIATE_OUTREACH)
        assert r.decision is PolicyDecision.REQUIRE_APPROVAL
        assert r.may_execute is False

    def test_deny_regulated_claim(self) -> None:
        r = self.policy.authorize(CommercialAction.MAKE_REGULATED_CLAIM)
        assert r.decision is PolicyDecision.DENY
        assert r.may_execute is False

    def test_deny_unsupported_guarantee(self) -> None:
        r = self.policy.authorize(CommercialAction.UNSUPPORTED_GUARANTEE)
        assert r.decision is PolicyDecision.DENY

    def test_deny_unapproved_channel(self) -> None:
        r = self.policy.authorize(CommercialAction.USE_UNAPPROVED_CHANNEL)
        assert r.decision is PolicyDecision.DENY

    def test_present_leados_standard_price_allowed(self) -> None:
        r = self.policy.authorize(
            CommercialAction.PRESENT_LEADOS_OFFER,
            context={"price_usd": 500},
        )
        assert r.decision is PolicyDecision.ALLOW

    def test_present_leados_out_of_policy_price_denied(self) -> None:
        r = self.policy.authorize(
            CommercialAction.PRESENT_LEADOS_OFFER,
            context={"price_usd": 50},
        )
        assert r.decision is PolicyDecision.DENY
        assert "Out-of-policy" in r.reason

    def test_activate_without_stripe_denied(self) -> None:
        r = self.policy.authorize(CommercialAction.ACTIVATE_SUBSCRIPTION)
        assert r.decision is PolicyDecision.DENY
        assert r.may_execute is False

    def test_activate_with_verified_stripe_allowed(self) -> None:
        r = self.policy.authorize(
            CommercialAction.ACTIVATE_SUBSCRIPTION,
            context={"stripe_verified": True, "stripe_event_id": "evt_test_123"},
        )
        assert r.decision is PolicyDecision.ALLOW
        assert r.may_execute is True

    def test_discount_requires_approval(self) -> None:
        r = self.policy.authorize(
            CommercialAction.APPLY_DISCOUNT,
            context={"discount_usd": 100},
        )
        assert r.decision is PolicyDecision.REQUIRE_APPROVAL

    def test_refund_above_threshold_requires_approval(self) -> None:
        r = self.policy.authorize(
            CommercialAction.REFUND_ABOVE_THRESHOLD,
            context={"refund_usd": 200},
        )
        assert r.decision is PolicyDecision.REQUIRE_APPROVAL

    def test_unknown_action_denied(self) -> None:
        r = self.policy.authorize("TOTALLY_UNKNOWN_ACTION")
        assert r.decision is PolicyDecision.DENY


class TestAuditStore:
    def test_append_and_chain(self) -> None:
        store = AuditStore()
        r1 = store.append(
            actor="system",
            action="SCORE_PROSPECT",
            target_type="prospect",
            target_id="p1",
            policy_decision="ALLOW",
            reason="ok",
            executed=True,
        )
        r2 = store.append(
            actor="system",
            action="GENERATE_PITCH",
            target_type="prospect",
            target_id="p1",
            policy_decision="ALLOW",
            reason="ok",
            executed=True,
        )
        assert r2.previous_hash == r1.record_hash
        ok, detail = store.verify_chain()
        assert ok is True
        assert "2 records" in detail

    def test_tamper_detection(self) -> None:
        store = AuditStore()
        store.append(
            actor="system",
            action="A",
            target_type="t",
            target_id="1",
            policy_decision="ALLOW",
            reason="x",
        )
        bad = store._records[0]
        from dataclasses import replace
        store._records[0] = replace(bad, reason="tampered")
        ok, detail = store.verify_chain()
        assert ok is False
        assert "mismatch" in detail.lower()

    def test_records_failed_executions(self) -> None:
        store = AuditStore()
        rec = store.append(
            actor="saphira",
            action="ACTIVATE_SUBSCRIPTION",
            target_type="customer",
            target_id="c1",
            policy_decision="ALLOW",
            reason="policy allowed but stripe failed",
            executed=False,
            event_id="evt_fail",
        )
        assert rec.executed is False
        assert store.filter(event_id="evt_fail")[0].executed is False


class TestCommercialStateMachine:
    def test_valid_happy_path_with_stripe(self) -> None:
        sm = CommercialStateMachine()
        path = [
            CommercialState.QUALIFIED,
            CommercialState.CONTACTED,
            CommercialState.ENGAGED,
            CommercialState.SALES_CONVERSATION,
            CommercialState.OFFER_PRESENTED,
            CommercialState.CHECKOUT_CREATED,
            CommercialState.PAYMENT_PENDING,
        ]
        for s in path:
            sm.transition(s)
        with pytest.raises(InvalidTransition):
            sm.transition(CommercialState.CUSTOMER, stripe_verified=False)
        result = sm.transition(CommercialState.CUSTOMER, stripe_verified=True)
        assert result.resulting is CommercialState.CUSTOMER

    def test_prospect_to_active_forbidden(self) -> None:
        sm = CommercialStateMachine()
        with pytest.raises(InvalidTransition):
            sm.transition(CommercialState.ACTIVE)

    def test_payment_pending_to_customer_without_stripe_rejected(self) -> None:
        sm = CommercialStateMachine(initial=CommercialState.PAYMENT_PENDING)
        ok, reason = sm.can_transition(CommercialState.CUSTOMER, stripe_verified=False)
        assert ok is False
        assert "verified Stripe" in reason


def _sign_payload(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    ts = timestamp if timestamp is not None else int(time.time())
    signed_payload = f"{ts}.".encode("utf-8") + payload
    sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


class TestStripeWebhookVerifier:
    SECRET = "whsec_test_secret_saphira"

    def _make_event_payload(
        self,
        event_id: str = "evt_test_001",
        event_type: str = "checkout.session.completed",
    ) -> bytes:
        body = {
            "id": event_id,
            "object": "event",
            "type": event_type,
            "data": {"object": {"id": "cs_test", "customer": "cus_test"}},
        }
        return json.dumps(body).encode("utf-8")

    def test_missing_signature_rejected(self) -> None:
        v = StripeWebhookVerifier(webhook_secret=self.SECRET)
        with pytest.raises(StripeWebhookError) as ei:
            v.construct_event(self._make_event_payload(), None)
        assert ei.value.status_code == 401

    def test_invalid_signature_rejected(self) -> None:
        v = StripeWebhookVerifier(webhook_secret=self.SECRET)
        payload = self._make_event_payload()
        with pytest.raises(StripeWebhookError) as ei:
            v.construct_event(payload, "t=1,v1=deadbeef")
        assert ei.value.status_code == 401

    def test_missing_secret_rejected(self) -> None:
        v = StripeWebhookVerifier(webhook_secret="")
        with pytest.raises(StripeWebhookError) as ei:
            v.construct_event(self._make_event_payload(), "t=1,v1=abc")
        assert ei.value.status_code == 500

    def test_valid_signature_accepted(self) -> None:
        v = StripeWebhookVerifier(webhook_secret=self.SECRET)
        payload = self._make_event_payload()
        header = _sign_payload(payload, self.SECRET)
        event = v.construct_event(payload, header)
        assert event["id"] == "evt_test_001"
        assert event["type"] == "checkout.session.completed"

    def test_verified_event_activates_customer(self) -> None:
        audit = AuditStore()
        machines = {
            "cust_1": CommercialStateMachine(initial=CommercialState.PAYMENT_PENDING)
        }
        v = StripeWebhookVerifier(
            webhook_secret=self.SECRET,
            audit=audit,
            state_machines=machines,
        )
        event = {
            "id": "evt_activate_1",
            "type": "checkout.session.completed",
            "data": {"object": {}},
        }
        result = v.process_verified_event(event, target_id="cust_1")
        assert result.accepted is True
        assert result.state_transition == "PAYMENT_PENDING→CUSTOMER"
        assert machines["cust_1"].state is CommercialState.CUSTOMER
        ok, _ = audit.verify_chain()
        assert ok is True
        executed = [r for r in audit.records if r.executed]
        assert len(executed) >= 1

    def test_duplicate_event_idempotent(self) -> None:
        machines = {
            "cust_2": CommercialStateMachine(initial=CommercialState.PAYMENT_PENDING)
        }
        v = StripeWebhookVerifier(webhook_secret=self.SECRET, state_machines=machines)
        event = {"id": "evt_dup", "type": "checkout.session.completed", "data": {}}
        r1 = v.process_verified_event(event, target_id="cust_2")
        r2 = v.process_verified_event(event, target_id="cust_2")
        assert r1.accepted is True
        assert r2.accepted is False
        assert "Duplicate" in r2.reason
        assert machines["cust_2"].state is CommercialState.CUSTOMER

    def test_non_activation_event_ignored(self) -> None:
        v = StripeWebhookVerifier(webhook_secret=self.SECRET)
        event = {"id": "evt_other", "type": "customer.updated", "data": {}}
        result = v.process_verified_event(event, target_id="cust_x")
        assert result.accepted is False
        assert "Non-activation" in result.reason

    def test_activation_from_wrong_state_rejected(self) -> None:
        machines = {
            "cust_3": CommercialStateMachine(initial=CommercialState.PROSPECT)
        }
        v = StripeWebhookVerifier(webhook_secret=self.SECRET, state_machines=machines)
        event = {"id": "evt_bad_state", "type": "checkout.session.completed", "data": {}}
        result = v.process_verified_event(event, target_id="cust_3")
        assert result.accepted is False
        assert machines["cust_3"].state is CommercialState.PROSPECT


class TestGovernancePath:
    def test_deny_never_executes(self) -> None:
        policy = CommercialAuthorityPolicy()
        audit = AuditStore()
        result = policy.authorize(CommercialAction.MAKE_REGULATED_CLAIM)
        assert result.may_execute is False
        audit.append(
            actor="saphira",
            action=result.action.value,
            target_type="claim",
            target_id="c1",
            policy_decision=result.decision.value,
            reason=result.reason,
            executed=False,
        )
        assert all(not r.executed for r in audit.records)

    def test_require_approval_never_executes(self) -> None:
        policy = CommercialAuthorityPolicy()
        result = policy.authorize(CommercialAction.INITIATE_OUTREACH)
        assert result.decision is PolicyDecision.REQUIRE_APPROVAL
        assert result.may_execute is False

    def test_allow_may_execute_and_is_audited(self) -> None:
        policy = CommercialAuthorityPolicy()
        audit = AuditStore()
        result = policy.authorize(CommercialAction.SCORE_PROSPECT)
        assert result.may_execute is True
        rec = audit.append(
            actor="saphira",
            action=result.action.value,
            target_type="prospect",
            target_id="p1",
            policy_decision=result.decision.value,
            reason=result.reason,
            executed=True,
        )
        assert rec.executed is True
        ok, _ = audit.verify_chain()
        assert ok is True
