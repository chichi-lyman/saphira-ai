"""Adversarial regression tests for Saphira's execution boundary."""

from core.hardening import Action, ActionClass, Decision, HardeningKernel


def make_action(
    name="research", action_class=ActionClass.READ, key="one", tenant="tenant-a", actor="user-a"
):
    return Action(
        name=name,
        action_class=action_class,
        tenant_id=tenant,
        actor_id=actor,
        idempotency_key=key,
    )


def test_read_action_is_allowed_once():
    kernel = HardeningKernel()
    first = kernel.evaluate(make_action())
    second = kernel.evaluate(make_action())

    assert first.decision is Decision.ALLOW
    assert second.decision is Decision.DENY
    assert second.reason == "duplicate_execution"


def test_external_action_requires_human_approval():
    kernel = HardeningKernel()
    decision = kernel.evaluate(make_action("send_email", ActionClass.EXTERNAL))

    assert decision.decision is Decision.REQUIRE_APPROVAL
    assert decision.reason == "approval_required"


def test_approval_is_recorded_and_cannot_be_replayed():
    kernel = HardeningKernel()
    pending = kernel.evaluate(make_action("send_email", ActionClass.EXTERNAL))
    approved = kernel.record_approved(pending)

    assert approved.decision is Decision.ALLOW

    replay = kernel.evaluate(make_action("send_email", ActionClass.EXTERNAL))
    assert replay.decision is Decision.DENY
    assert replay.reason == "duplicate_execution"


def test_financial_action_requires_approval():
    kernel = HardeningKernel()
    result = kernel.evaluate(make_action("charge_customer", ActionClass.FINANCIAL))
    assert result.decision is Decision.REQUIRE_APPROVAL


def test_destructive_action_requires_approval():
    kernel = HardeningKernel()
    result = kernel.evaluate(make_action("delete_workspace", ActionClass.DESTRUCTIVE))
    assert result.decision is Decision.REQUIRE_APPROVAL


def test_explicitly_denied_action_cannot_execute():
    kernel = HardeningKernel(denied_actions=frozenset({"export_credentials"}))
    result = kernel.evaluate(make_action("export_credentials", ActionClass.READ))
    assert result.decision is Decision.DENY
    assert result.reason == "action_denied_by_policy"


def test_missing_identity_fails_closed():
    kernel = HardeningKernel()
    result = kernel.evaluate(make_action(tenant="", actor="user-a"))
    assert result.decision is Decision.DENY
    assert result.reason == "missing_execution_identity"


def test_tenants_get_distinct_execution_ids():
    kernel = HardeningKernel()
    a = kernel.evaluate(make_action(tenant="tenant-a"))
    b = kernel.evaluate(make_action(tenant="tenant-b"))

    assert a.execution_id != b.execution_id
    assert a.decision is Decision.ALLOW
    assert b.decision is Decision.ALLOW


def test_model_cannot_self_grant_financial_authority():
    kernel = HardeningKernel()
    action = make_action(
        name="charge_customer",
        action_class=ActionClass.FINANCIAL,
        key="model-claimed-authority",
    )
    action = Action(
        **{**action.__dict__, "metadata": {"authorized_by_model": "true"}}
    )

    result = kernel.evaluate(action)
    assert result.decision is Decision.REQUIRE_APPROVAL


def test_execution_window_is_bounded():
    kernel = HardeningKernel(max_execution_seconds=30)
    result = kernel.evaluate(make_action())
    assert result.expires_at - result.action.requested_at > 0
    assert result.expires_at <= result.action.requested_at + 31
