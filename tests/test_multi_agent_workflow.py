"""Tests for multi-agent workflow engine and skill workers.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import pytest

from src.orchestration.multi_agent_workflow import (
    MultiAgentWorkflowEngine,
    build_research_code_validate,
    build_analyze_architect_review,
    build_secure_delivery,
    NodeStatus,
)
from src.orchestration.workers import default_workers
from src.orchestration.executor import TaskExecutor
from src.orchestration.task import TaskStatus
from src.platform.entitlements.metering import EntitlementRegistry


@pytest.mark.asyncio
async def test_research_code_validate_completes():
    workers = default_workers()
    executor = TaskExecutor(workers=workers)
    engine = MultiAgentWorkflowEngine(executor=executor)

    task, graph, meter = await engine.run_research_code_validate(
        "Build a small API that lists health status"
    )

    assert task.status == TaskStatus.COMPLETED
    assert graph.is_complete()
    assert not graph.failed_nodes()
    assert len(task.artifacts) >= 3
    statuses = {n.name: n.status for n in graph.nodes.values()}
    assert statuses["research"] == NodeStatus.COMPLETED
    assert statuses["draft_spec"] == NodeStatus.COMPLETED
    assert statuses["implement"] == NodeStatus.COMPLETED
    assert statuses["validate"] == NodeStatus.COMPLETED


@pytest.mark.asyncio
async def test_analyze_architect_review_fanout():
    workers = default_workers()
    executor = TaskExecutor(workers=workers)
    engine = MultiAgentWorkflowEngine(executor=executor)

    task, graph, meter = await engine.run_analyze_architect_review(
        "Review the multi-agent pipeline and suggest metrics"
    )

    assert task.status == TaskStatus.COMPLETED
    names = {n.name for n in graph.nodes.values()}
    assert "data_analysis" in names
    assert "systems_architecture" in names
    assert "code_review" in names
    assert "synthesize" in names
    agents = {n.name: n.agent for n in graph.nodes.values()}
    assert agents["code_review"] == "code_reviewer_agent"
    assert agents["systems_architecture"] == "systems_architect_agent"
    assert agents["data_analysis"] == "data_analyst_agent"


@pytest.mark.asyncio
async def test_secure_delivery_includes_auditor():
    workers = default_workers()
    executor = TaskExecutor(workers=workers)
    engine = MultiAgentWorkflowEngine(executor=executor)

    task, graph, meter = await engine.run_secure_delivery(
        "Ship a new webhook endpoint safely"
    )
    assert task.status == TaskStatus.COMPLETED
    agents = {n.name: n.agent for n in graph.nodes.values()}
    assert agents["security_audit"] == "security_auditor_agent"
    assert "security_auditor" in default_workers()


@pytest.mark.asyncio
async def test_metering_blocks_when_quota_exhausted():
    reg = EntitlementRegistry()
    reg.assign("t1", "free")
    ent = reg.get("t1")
    assert ent is not None
    # Exhaust free workflow quota
    for _ in range(ent.plan.workflow_runs_per_day):
        assert ent.consume("workflow_runs_day")

    workers = default_workers()
    engine = MultiAgentWorkflowEngine(
        executor=TaskExecutor(workers=workers),
        entitlements_registry=reg,
    )
    task, graph, meter = await engine.run_research_code_validate(
        "Should be blocked", tenant_id="t1"
    )
    assert task.status == TaskStatus.FAILED
    assert meter is not None
    assert meter.get("error") == "quota_exceeded"


@pytest.mark.asyncio
async def test_super_saphira_allows_more_runs():
    reg = EntitlementRegistry()
    reg.assign("vip", "super_saphira")
    workers = default_workers()
    engine = MultiAgentWorkflowEngine(
        executor=TaskExecutor(workers=workers),
        entitlements_registry=reg,
    )
    task, graph, meter = await engine.run_research_code_validate(
        "Allowed on super", tenant_id="vip"
    )
    assert task.status == TaskStatus.COMPLETED
    assert meter is not None
    assert meter.get("plan") == "super_saphira"
    assert meter.get("remaining_workflow_runs", 0) >= 0
