"""Platform layer unit tests."""

from __future__ import annotations

import pytest

from src.platform.policy import AutonomyPolicy, AutonomyLevel, CounterfactualPreview
from src.platform.memory import memory_store
from src.platform.voice import voice_sessions, AvatarState
from src.platform.entitlements import entitlements
from src.platform.identity import identity_service, Principal
from src.platform.evidence import issue_receipt
from src.platform.swarm import HierarchicalSwarm, SwarmBudget
from src.platform.devices import matter_bridge, DeviceCommand, offline_queue
from src.platform.plugins import plugin_registry, PluginSpec
from src.platform.observability_ext import model_router
from src.platform.sdk import SaphiraClient


def test_autonomy_l1_requires_confirm():
    policy = AutonomyPolicy()
    d = policy.decide("payment", {})
    assert d.level == AutonomyLevel.L1_CONFIRM_FIRST
    assert d.requires_confirmation is True
    d2 = policy.decide("payment", {"confirmed": True})
    assert d2.requires_confirmation is False


def test_counterfactual_preview():
    p = CounterfactualPreview.build("pay invoice", "payment", ["stripe"], side_effects=["charge card"])
    assert "Confirm" in p["title"]
    assert p["capability"] == "payment"


def test_memory_tenant_isolation():
    memory_store.add("t1", "u1", "secret for t1", kind="episodic")
    memory_store.add("t2", "u2", "secret for t2", kind="episodic")
    rows = memory_store.list_for_user("t1", "u1")
    assert all(r.tenant_id == "t1" for r in rows)


def test_memory_distill_semantic():
    memory_store.add("td", "ud", "A sufficiently long episodic memory about project alpha goals.", confidence=0.9)
    promoted = memory_store.distill_semantic("td", "ud")
    assert promoted[0].kind == "semantic"


def test_voice_session_state_machine():
    sess = voice_sessions.create("t", "u")
    voice_sessions.set_state(sess.session_id, AvatarState.CONFIRM)
    assert voice_sessions.get(sess.session_id).avatar_state == AvatarState.CONFIRM


def test_entitlements_quota():
    ent = entitlements.assign("tenant-meter", "free")
    assert ent.consume("api_calls", 1) is True
    ent.usage.seats_used = ent.plan.seats
    assert ent.check("seats", 1) is False


def test_identity_api_key_and_rbac():
    token = identity_service.issue_api_key("tenant-x")
    assert identity_service.verify_api_key(token) is not None
    principal = Principal("user1", "tenant-x", roles=["operator"])
    assert principal.can("agent:invoke")


def test_action_receipt_chain():
    r = issue_receipt("t", "actor", "payment", "REQUIRE_APPROVAL", "m1", {"x": 1})
    assert len(r.chain_hash()) == 64


@pytest.mark.asyncio
async def test_hierarchical_swarm_budget():
    async def agent_a(ctx):
        return {"status": "ok", "agent": "a"}

    async def agent_b(ctx):
        return {"status": "ok", "agent": "b"}

    swarm = HierarchicalSwarm("lead", {"a": agent_a, "b": agent_b}, SwarmBudget(max_agents=2, max_seconds=5))
    result = await swarm.run("plan evening")
    assert result.status == "success"
    assert len(result.agents_run) == 2


def test_matter_bridge_l1_for_unlock():
    plan = matter_bridge.plan(DeviceCommand("lock-1", "unlock", {}), confirmed=False)
    assert plan["status"] == "needs_confirmation"


def test_offline_queue():
    offline_queue.enqueue("t", "u", "dim the lights")
    assert offline_queue.pending_count() >= 1
    offline_queue.drain()
    assert offline_queue.pending_count() == 0


def test_plugin_sandbox_high_risk():
    plugin_registry.register(PluginSpec(name="shell", version="1.0", risk_tier="high"))
    assert plugin_registry.invoke("shell", {"cmd": "ls"})["status"] == "needs_confirmation"


def test_model_router_and_sdk_dry_run():
    assert model_router.resolve("code").provider
    decision = SaphiraClient().dry_run_capability("payment", {"intent": "pay", "tools": ["stripe"]})
    assert decision["requires_confirmation"] is True


def test_biometric_stress_levels():
    from src.platform.biometrics import biometric_stress
    low = biometric_stress.analyze({"hrv": 90, "resting_hr": 55, "sleep_score": 95})
    assert low.stress_level == "low"
    high = biometric_stress.analyze({"hrv": 25, "resting_hr": 100, "sleep_score": 30})
    assert high.stress_level == "high"
