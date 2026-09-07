from concurrent.futures import ThreadPoolExecutor

from core.hardening.kernel import Action, ActionClass, Decision, HardeningKernel


def make_action(i: int, action_class: ActionClass = ActionClass.READ) -> Action:
    return Action(
        name=f"read_{i}",
        action_class=action_class,
        tenant_id=f"tenant-{i % 10}",
        actor_id=f"actor-{i % 100}",
        idempotency_key=f"request-{i}",
    )


def test_concurrent_distinct_actions_are_isolated():
    kernel = HardeningKernel()
    with ThreadPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(lambda i: kernel.evaluate(make_action(i)), range(1000)))
    assert all(r.decision is Decision.ALLOW for r in results)
    assert len({r.execution_id for r in results}) == 1000


def test_duplicate_action_is_fail_closed():
    kernel = HardeningKernel()
    action = make_action(1)
    assert kernel.evaluate(action).decision is Decision.ALLOW
    assert kernel.evaluate(action).decision is Decision.DENY
    assert kernel.evaluate(action).reason == "duplicate_execution"


def test_consequential_actions_require_approval():
    kernel = HardeningKernel()
    for action_class in (
        ActionClass.EXTERNAL,
        ActionClass.FINANCIAL,
        ActionClass.DESTRUCTIVE,
    ):
        result = kernel.evaluate(make_action(2, action_class))
        assert result.decision is Decision.REQUIRE_APPROVAL


def test_model_cannot_self_authorize():
    kernel = HardeningKernel()
    action = Action(
        name="send_campaign",
        action_class=ActionClass.EXTERNAL,
        tenant_id="tenant-a",
        actor_id="model:saphira",
        idempotency_key="x",
        metadata={"approved": "true", "authority": "system"},
    )
    assert kernel.evaluate(action).decision is Decision.REQUIRE_APPROVAL


def test_missing_identity_denies():
    kernel = HardeningKernel()
    action = Action(
        name="read_private_data",
        action_class=ActionClass.READ,
        tenant_id="",
        actor_id="",
        idempotency_key="",
    )
    assert kernel.evaluate(action).decision is Decision.DENY
