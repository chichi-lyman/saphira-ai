# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Tests for Elite Agent Upgrade — cycle detection, isolation, memory, routing

import pytest
import asyncio
from src.core.task_graph import TaskGraph, TaskNode, TaskStatus
from src.memory.nova_aethrea_store import NovaAethreaMemoryStore, MemoryRecord, MemoryKind
from src.core.elite_agent_base import EliteAgentBase
from src.agents.elite_core_agents import SaphiraCore, AgentTwo
from src.agents.elite_specialists import Apex


@pytest.mark.asyncio
async def test_task_graph_cycle_detection():
    g = TaskGraph("test")
    a = TaskNode(id="a", capability="x", agent_key="saphira", payload={})
    b = TaskNode(id="b", capability="y", agent_key="aura", payload={}, depends_on=["a"])
    c = TaskNode(id="c", capability="z", agent_key="agent_two", payload={}, depends_on=["b"])
    # Introduce cycle
    a.depends_on = ["c"]
    g.add(a)
    g.add(b)
    g.add(c)
    assert g.has_cycle() is True


@pytest.mark.asyncio
async def test_task_graph_no_cycle():
    g = TaskGraph("test")
    a = TaskNode(id="a", capability="x", agent_key="saphira", payload={})
    b = TaskNode(id="b", capability="y", agent_key="aura", payload={}, depends_on=["a"])
    g.add(a)
    g.add(b)
    assert g.has_cycle() is False
    ready = g.ready_wave()
    assert len(ready) == 1
    assert ready[0].id == "a"


@pytest.mark.asyncio
async def test_memory_write_and_recall():
    store = NovaAethreaMemoryStore()
    rec = MemoryRecord(
        id="m1",
        tenant_id="default",
        kind=MemoryKind.PREFERENCE,
        content={"pref": "likes quiet mornings"},
    )
    rid = await store.write(rec)
    assert rid == "m1"
    hits = await store.recall("default", "quiet mornings", top_k=5)
    assert len(hits) >= 1
    assert hits[0].content["pref"] == "likes quiet mornings"


@pytest.mark.asyncio
async def test_agent_isolation_token():
    agent = SaphiraCore()
    result = await agent.safe_run({"text": "hello", "tenant_id": "t1"})
    assert "isolation_token" in result
    assert result["status"] in ("success", "recovered_from_failure")
    assert result.get("agent") == "saphira"


@pytest.mark.asyncio
async def test_security_gate_blocks_high_risk():
    agent = AgentTwo()
    result = await agent.safe_run({
        "text": "delete everything",
        "intent": "delete",
        "confirmed": False,
    })
    assert result["status"] == "blocked"
    assert "confirmation" in result.get("message", "").lower() or result.get("requires") == "user_confirmation"


@pytest.mark.asyncio
async def test_apex_specialist():
    agent = Apex()
    result = await agent.safe_run({"text": "grow revenue next quarter"})
    assert result["status"] == "success"
    assert "recommendation" in result
