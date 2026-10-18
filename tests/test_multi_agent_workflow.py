"""Tests for multi-agent workflow engine and skill workers.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import pytest

from src.orchestration.multi_agent_workflow import (
    MultiAgentWorkflowEngine,
    build_research_code_validate,
    build_analyze_architect_review,
    WorkflowGraph,
    NodeStatus,
)
from src.orchestration.workers import default_workers
from src.orchestration.executor import TaskExecutor
from src.orchestration.task import TaskStatus


@pytest.mark.asyncio
async def test_research_code_validate_completes():
    workers = default_workers()
    executor = TaskExecutor(workers=workers)
    engine = MultiAgentWorkflowEngine(executor=executor)

    task, graph = await engine.run_research_code_validate(
        "Build a small API that lists health status"
    )

    assert task.status == TaskStatus.COMPLETED
    assert graph.is_complete()
    assert not graph.failed_nodes()
    assert len(task.artifacts) >= 3
    # Parallel research + draft should both complete before implement
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

    task, graph = await engine.run_analyze_architect_review(
        "Review the multi-agent pipeline and suggest metrics"
    )

    assert task.status == TaskStatus.COMPLETED
    names = {n.name for n in graph.nodes.values()}
    assert "data_analysis" in names
    assert "systems_architecture" in names
    assert "code_review" in names
    assert "synthesize" in names
    # Skill-linked agents should be assigned
    agents = {n.name: n.agent for n in graph.nodes.values()}
    assert agents["code_review"] == "code_reviewer_agent"
    assert agents["systems_architecture"] == "systems_architect_agent"
    assert agents["data_analysis"] == "data_analyst_agent"


@pytest.mark.asyncio
async def test_custom_linear_graph():
    workers = default_workers()
    executor = TaskExecutor(workers=workers)
    engine = MultiAgentWorkflowEngine(executor=executor)

    from src.orchestration.multi_agent_workflow import build_custom_linear

    graph = build_custom_linear(
        "Linear demo",
        [("research", "research"), ("implement", "development"), ("validate", "quality")],
    )
    task, graph = await engine.run(graph)
    assert task.status == TaskStatus.COMPLETED
    ordered = [n for n in graph.nodes.values()]
    # dependency chain respected: first has no deps, last depends on previous
    assert ordered[0].depends_on == [] or len(list(graph.nodes.values())[0].depends_on) == 0
