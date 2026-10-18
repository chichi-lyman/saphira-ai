"""Multi-agent workflow engine for Saphira.

Copyright © 2026 Chelsea Megan Woods

Supports:
- Dynamic DAG construction (sequential + parallel fan-out / fan-in)
- Structured handoff envelopes (never expose codenames to end users)
- Research → Code → Validate pattern as a first-class template
- Integration with TaskPlanner / AgentRegistry / TaskExecutor
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable
from uuid import uuid4

from .task import Task, TaskStatus, utc_now
from .registry import AgentRegistry, AgentSpec
from .executor import TaskExecutor, AgentWorker, ExecutionResult
from .planner import TaskPlanner

logger = logging.getLogger("SaphiraMultiAgentWorkflow")


class NodeStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class HandoffEnvelope:
    """Shared message envelope — internal only; never shown to users."""

    trace_id: str
    from_agent: str
    to_agent: str
    task_id: str
    objective: str
    constraints: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    policy: str = "ALLOW"
    deadline_ms: int | None = None
    reply_channel: str = "orchestrator"
    status: str = "ACCEPTED"


@dataclass
class WorkflowNode:
    id: str
    name: str
    capability: str
    agent: str | None = None
    depends_on: list[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    parallel_group: str | None = None


@dataclass
class WorkflowGraph:
    """Directed acyclic graph of agent steps."""

    id: str = field(default_factory=lambda: f"wf_{uuid4().hex[:10]}")
    objective: str = ""
    nodes: dict[str, WorkflowNode] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)

    def add_node(
        self,
        name: str,
        capability: str,
        depends_on: list[str] | None = None,
        parallel_group: str | None = None,
        node_id: str | None = None,
    ) -> str:
        nid = node_id or f"node_{uuid4().hex[:8]}"
        self.nodes[nid] = WorkflowNode(
            id=nid,
            name=name,
            capability=capability,
            depends_on=list(depends_on or []),
            parallel_group=parallel_group,
        )
        for dep in self.nodes[nid].depends_on:
            self.edges.append((dep, nid))
        return nid

    def ready_nodes(self) -> list[WorkflowNode]:
        ready = []
        for node in self.nodes.values():
            if node.status != NodeStatus.PENDING:
                continue
            deps_ok = all(
                self.nodes[d].status == NodeStatus.COMPLETED
                for d in node.depends_on
                if d in self.nodes
            )
            if deps_ok:
                ready.append(node)
        return ready

    def is_complete(self) -> bool:
        return all(
            n.status in {NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED}
            for n in self.nodes.values()
        )

    def failed_nodes(self) -> list[WorkflowNode]:
        return [n for n in self.nodes.values() if n.status == NodeStatus.FAILED]


# ---------------------------------------------------------------------------
# Workflow templates
# ---------------------------------------------------------------------------

def build_research_code_validate(objective: str) -> WorkflowGraph:
    """Classic parallel-friendly pattern: research ‖ draft → code → validate."""
    g = WorkflowGraph(objective=objective)
    research = g.add_node("research", "research", parallel_group="fanout_1")
    draft = g.add_node("draft_spec", "content", parallel_group="fanout_1")
    # Fan-in: code depends on both research and draft
    code = g.add_node("implement", "development", depends_on=[research, draft])
    validate = g.add_node("validate", "quality", depends_on=[code])
    return g


def build_analyze_architect_review(objective: str) -> WorkflowGraph:
    """Data analysis + systems architecture + code review in parallel, then synthesize."""
    g = WorkflowGraph(objective=objective)
    data = g.add_node("data_analysis", "analytics", parallel_group="fanout_1")
    arch = g.add_node("systems_architecture", "architecture", parallel_group="fanout_1")
    review = g.add_node("code_review", "code_review", parallel_group="fanout_1")
    synthesize = g.add_node(
        "synthesize",
        "reasoning",
        depends_on=[data, arch, review],
    )
    return g


def build_custom_linear(objective: str, steps: list[tuple[str, str]]) -> WorkflowGraph:
    """Linear chain from (name, capability) pairs."""
    g = WorkflowGraph(objective=objective)
    prev: str | None = None
    for name, cap in steps:
        nid = g.add_node(name, cap, depends_on=[prev] if prev else None)
        prev = nid
    return g


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class MultiAgentWorkflowEngine:
    """
    Executes WorkflowGraph nodes with dependency resolution and parallel groups.

    Workers are looked up via AgentRegistry routing on capability tags.
    Results are merged into a Task for downstream verification / memory.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        executor: TaskExecutor | None = None,
        max_parallel: int = 6,
        timeout_seconds: float = 300,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.executor = executor or TaskExecutor()
        self.max_parallel = max_parallel
        self.timeout_seconds = timeout_seconds
        self._ensure_skill_capabilities()

    def _ensure_skill_capabilities(self) -> None:
        """Register skill-linked agents if not already present."""
        extras = (
            ("code_reviewer_agent", {"code_review", "development", "quality"}, 15, "Saphira Code Reviewer skill"),
            ("systems_architect_agent", {"architecture", "system", "development"}, 15, "Saphira Systems Architect skill"),
            ("data_analyst_agent", {"analytics", "research", "stem"}, 15, "Saphira Data Analyst skill"),
        )
        for name, caps, priority, desc in extras:
            if name not in self.registry.agents:
                self.registry.register(
                    AgentSpec(name, frozenset(caps), priority, desc)
                )

    def route_graph(self, graph: WorkflowGraph) -> None:
        """Assign agents to nodes from the capability registry."""
        for node in graph.nodes.values():
            candidates = [
                a
                for a in self.registry.agents.values()
                if node.capability in a.capabilities
            ]
            candidates.sort(key=lambda a: a.priority)
            if candidates:
                node.agent = candidates[0].name

    async def _run_node(
        self,
        node: WorkflowNode,
        graph: WorkflowGraph,
        task: Task,
        upstream: dict[str, Any],
    ) -> None:
        node.status = NodeStatus.RUNNING
        worker = self.executor.workers.get(node.agent) if node.agent else None

        envelope = HandoffEnvelope(
            trace_id=graph.id,
            from_agent="novareign",
            to_agent=node.agent or "unassigned",
            task_id=task.id,
            objective=graph.objective,
            inputs={"upstream": upstream, "node": node.name},
            policy="ALLOW",
        )

        step = {
            "id": node.id,
            "name": node.name,
            "capability": node.capability,
            "agent": node.agent,
            "status": "running",
            "envelope": envelope.__dict__,
        }

        try:
            if worker:
                result = await asyncio.wait_for(
                    worker.execute(task, step),
                    timeout=self.timeout_seconds,
                )
                node.result = result or {"status": "ok", "agent": node.agent}
            else:
                # Soft stub when worker not connected — keeps graph progressing in tests/dev
                node.result = {
                    "status": "stub",
                    "agent": node.agent,
                    "message": f"[{node.name}] processed (worker not connected)",
                    "capability": node.capability,
                }
                logger.info("Node %s stubbed — no worker for %s", node.id, node.agent)
            node.status = NodeStatus.COMPLETED
            task.emit("workflow_node_completed", node=node.id, agent=node.agent)
        except Exception as exc:
            node.status = NodeStatus.FAILED
            node.error = f"{type(exc).__name__}: {exc}"
            task.emit("workflow_node_failed", node=node.id, error=node.error)
            logger.exception("Workflow node %s failed", node.id)

    async def run(
        self,
        graph: WorkflowGraph,
        context: dict[str, Any] | None = None,
    ) -> tuple[Task, WorkflowGraph]:
        """Execute the full graph with parallel groups respected."""
        task = Task(objective=graph.objective, context=context or {})
        task.set_status(TaskStatus.RUNNING)
        self.route_graph(graph)

        # Materialize plan steps for observability
        for node in graph.nodes.values():
            task.add_step(node.name, node.capability, agent=node.agent, workflow_node=node.id)

        sem = asyncio.Semaphore(self.max_parallel)

        while not graph.is_complete():
            ready = graph.ready_nodes()
            if not ready:
                # Deadlock or all remaining depend on failed nodes
                for n in graph.nodes.values():
                    if n.status == NodeStatus.PENDING:
                        n.status = NodeStatus.SKIPPED
                        n.error = "upstream_failed_or_cycle"
                break

            async def bounded(node: WorkflowNode):
                async with sem:
                    upstream = {
                        dep: graph.nodes[dep].result
                        for dep in node.depends_on
                        if dep in graph.nodes and graph.nodes[dep].result
                    }
                    await self._run_node(node, graph, task, upstream)

            await asyncio.gather(*(bounded(n) for n in ready))

        if graph.failed_nodes():
            task.set_status(TaskStatus.FAILED)
            task.errors.extend(n.error or "unknown" for n in graph.failed_nodes())
        else:
            task.set_status(TaskStatus.VERIFYING)
            task.verification = {
                "passed": True,
                "checks": ["workflow_graph_complete"],
                "nodes": len(graph.nodes),
            }
            # Collect artifacts
            for n in graph.nodes.values():
                if n.result:
                    task.artifacts.append(n.result)
            task.set_status(TaskStatus.COMPLETED)
            task.emit("workflow_completed", workflow_id=graph.id)

        return task, graph

    async def run_research_code_validate(
        self, objective: str, context: dict[str, Any] | None = None
    ) -> tuple[Task, WorkflowGraph]:
        graph = build_research_code_validate(objective)
        return await self.run(graph, context)

    async def run_analyze_architect_review(
        self, objective: str, context: dict[str, Any] | None = None
    ) -> tuple[Task, WorkflowGraph]:
        graph = build_analyze_architect_review(objective)
        return await self.run(graph, context)
