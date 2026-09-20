# Copyright © 2026 Chelsea Megan Woods
"""Unit tests for PersistentMemoryStore ContextPack and specialist registry."""

from src.memory.persistent_store import PersistentMemoryStore
from src.core.specialist_registry import specialist_registry, EXTENDED_SPECIALISTS
from src.core.handoff_envelope import make_envelope, STATUS_NEED_APPROVAL


def test_context_pack_shape(tmp_path):
    store = PersistentMemoryStore(path=str(tmp_path / "mem.json"))
    store.set_fact("user.timezone", "America/New_York")
    store.set_preference("tone", "warm")
    pack = store.build_context_pack(task_id="t1", policy_grant="ALLOW")
    assert pack["task_id"] == "t1"
    assert pack["facts"]["user.timezone"] == "America/New_York"
    assert pack["preferences"]["tone"] == "warm"
    assert pack["policy_grant"] == "ALLOW"
    assert "history_slice" in pack
    assert "connector_health" in pack


def test_connector_health(tmp_path):
    store = PersistentMemoryStore(path=str(tmp_path / "mem2.json"))
    store.update_connector_health("mcp.calendar", status="ok", retries=0)
    health = store.get_connector_health()
    assert health["mcp.calendar"]["status"] == "ok"


def test_specialist_registry_policies():
    assert specialist_registry.policy_for("agent_apex") == "REQUIRE_APPROVAL"
    assert specialist_registry.policy_for("agent_cipher") == "ALLOW"
    specs = specialist_registry.list_specs()
    assert len(specs) >= 5
    assert "agent_apex" in EXTENDED_SPECIALISTS


def test_handoff_envelope():
    env = make_envelope(
        from_agent="nova_reign",
        to_agent="nova_aethrea",
        objective="load evening scene",
        policy="ALLOW",
    )
    assert env["from_agent"] == "nova_reign"
    assert env["to_agent"] == "nova_aethrea"
    assert env["policy"] == "ALLOW"
    assert STATUS_NEED_APPROVAL == "NEED_APPROVAL"
