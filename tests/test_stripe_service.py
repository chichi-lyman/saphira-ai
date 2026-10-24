"""Unit tests for Stripe helpers; never make live network calls."""
from __future__ import annotations

import os
import sys
import types

import pytest

from src.integrations import stripe_service


def test_checkout_requires_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("STRIPE_PRICE_MONTHLY", "price_test")
    with pytest.raises(stripe_service.StripeConfigurationError, match="STRIPE_SECRET_KEY"):
        stripe_service.create_subscription_checkout(
            customer_email="user@example.com",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            user_id="user-1",
            idempotency_key="checkout-user-1",
        )


def test_checkout_requires_price(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_not_real")
    monkeypatch.delenv("STRIPE_PRICE_MONTHLY", raising=False)
    monkeypatch.delenv("STRIPE_PRICE_ID", raising=False)
    with pytest.raises(stripe_service.StripeConfigurationError, match="PRICE"):
        stripe_service.create_subscription_checkout(
            customer_email="user@example.com",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            user_id="user-1",
            idempotency_key="checkout-user-1",
        )


def test_checkout_uses_idempotency_and_user_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}
    class Session:
        @staticmethod
        def create(**kwargs):
            calls.update(kwargs)
            return types.SimpleNamespace(id="cs_test_123", url="https://checkout.stripe.com/test")
    fake_stripe = types.SimpleNamespace(api_key=None, checkout=types.SimpleNamespace(Session=Session))
    monkeypatch.setitem(sys.modules, "stripe", fake_stripe)
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_not_real")
    monkeypatch.setenv("STRIPE_PRICE_MONTHLY", "price_test")
    result = stripe_service.create_subscription_checkout(
        customer_email=" user@example.com ",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        user_id="user-1",
        idempotency_key="checkout-user-1",
    )
    assert result == {"id": "cs_test_123", "url": "https://checkout.stripe.com/test"}
    assert calls["options"] == {"idempotency_key": "checkout-user-1"}
    assert calls["metadata"] == {"saphira_user_id": "user-1"}
    assert calls["mode"] == "subscription"


def test_webhook_requires_configured_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    with pytest.raises(stripe_service.StripeConfigurationError, match="STRIPE_WEBHOOK_SECRET"):
        stripe_service.verify_webhook(b"{}", "sig")
