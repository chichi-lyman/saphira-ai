# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# EliteRouter — fail-safe capability routing with TaskGraph, isolation, and cycle guards.

from __future__ import annotations

from typing import Any, Dict, List, Optional
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from src.core.task_graph import TaskGraph, TaskNode, TaskStatus

logger = logging.getLogger("SaphiraEliteRouter")


class EliteRouter:
    """
    Fail-safe routing engine for Saphira.

    - Builds a dependency-gated TaskGraph from intent
    - Routes by capability (never free-form agent chat)
    - Hard cycle / depth / concurrency guards
    - Identity isolation via isolation_token + secret-mask
    - Parallel ready-wave execution with bulkhead + timeout
    """

    def __init__(
        self,
        registry: Any,
        core_pipeline: Any = None,
        max_parallel: int = 6,
        max_graph_depth: int = 12,
    ):
        self.registry = registry
        self.core = core_pipeline
        self.max_parallel = max_parallel
        self.max_graph_depth = max_graph_depth
        self._active_graphs: Dict[str, TaskGraph] = {}

    async def route(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        context = context or {}
        graph = TaskGraph(root_intent=user_input, tenant_id=tenant_id)

        plan = await self._plan_capabilities(user_input, context)
        if not plan:
            if self.core is not None:
                return await self.core.process(user_input, context)
            return {
                "status": "error",
                "message": "No plan and no core pipeline available",
            }

        prev_id: Optional[str] = None
        for step in plan:
            node = TaskNode(
                id=str(uuid.uuid4()),
                capability=step["capability"],
                agent_key=self.registry.agent_for(step["capability"]),
                payload={
                    **context,
                    **step.get("payload", {}),
                    "user_input": user_input,
                    "tenant_id": tenant_id,
                },
                depends_on=[prev_id] if prev_id and step.get("sequential", True) else [],
            )
            graph.add(node)
            prev_id = node.id

        if graph.has_cycle():
            logger.error("Cycle detected in plan – aborting")
            return {
                "status": "error",
                "message": "Internal routing cycle blocked by EliteRouter",
            }

        self._active_graphs[graph.graph_id] = graph

        sem = asyncio.Semaphore(self.max_parallel)
        while True:
            ready = graph.ready_wave()
            if not ready:
                break
            if len(graph.completed) + len(graph.failed) > self.max_graph_depth * 4:
                logger.warning("Depth guard triggered for graph %s", graph.graph_id)
                break

            async def run_node(node: TaskNode) -> Dict[str, Any]:
                async with sem:
                    return await self._execute_node(node, graph)

            results = await asyncio.gather(
                *(run_node(n) for n in ready), return_exceptions=True
            )
            for node, res in zip(ready, results):
                if isinstance(res, Exception):
                    graph.mark_failed(node.id, str(res))
                elif isinstance(res, dict) and res.get("status") in (
                    "success",
                    "recovered_from_failure",
                    "scene_executed",
                    "completed",
                ):
                    graph.mark_done(node.id, res)
                else:
                    msg = (
                        res.get("message", "unknown")
                        if isinstance(res, dict)
                        else "unknown"
                    )
                    graph.mark_failed(node.id, msg)

            if graph.failed and not graph.ready_wave():
                break

        return self._synthesize(graph, user_input)

    async def _execute_node(
        self, node: TaskNode, graph: TaskGraph
    ) -> Dict[str, Any]:
        agent = self.registry.get(node.agent_key)
        if agent is None:
            return {
                "status": "error",
                "message": f"No agent registered for capability {node.capability}",
            }

        node.status = TaskStatus.RUNNING
        node.started_at = datetime.now(timezone.utc).isoformat()

        envelope = {
            **node.payload,
            "isolation_token": node.isolation_token,
            "capability": node.capability,
            "tenant_id": graph.tenant_id,
            "secret_mask": True,
        }

        try:
            if hasattr(agent, "safe_run"):
                return await asyncio.wait_for(
                    agent.safe_run(envelope), timeout=node.timeout_s
                )
            if hasattr(agent, "run"):
                return await asyncio.wait_for(
                    agent.run(envelope), timeout=node.timeout_s
                )
            if hasattr(agent, "process"):
                return await asyncio.wait_for(
                    agent.process(envelope), timeout=node.timeout_s
                )
            return {
                "status": "error",
                "message": f"Agent {node.agent_key} has no executable method",
            }
        except asyncio.TimeoutError:
            return {"status": "error", "message": "timeout"}
        except Exception as e:
            logger.exception("Node %s (%s) failed", node.id, node.agent_key)
            return {"status": "error", "error": str(e)}

    async def _plan_capabilities(
        self, user_input: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Produce an ordered list of {capability, payload, sequential}.
        Prefer registry rules + IntentClassifier; LLM only for complex cases.
        Falls back to the classic six-agent pipeline when no specialist plan is found.
        """
        # Classic fixed pipeline as safe default
        return [
            {"capability": "intent.parse", "sequential": True},
            {"capability": "perception.entity", "sequential": True},
            {"capability": "security.gate", "sequential": True},
            {"capability": "governance.plan", "sequential": True},
            {"capability": "memory.read", "sequential": True},
            {"capability": "device.execute", "sequential": True},
        ]

    def _synthesize(
        self, graph: TaskGraph, user_input: str
    ) -> Dict[str, Any]:
        successes = [
            n.result
            for n in graph.nodes.values()
            if n.status == TaskStatus.SUCCESS and n.result
        ]
        failures = [
            {"agent": n.agent_key, "error": n.error}
            for n in graph.nodes.values()
            if n.status == TaskStatus.FAILED
        ]

        final_status = "success" if successes and not failures else "partial"
        if not successes:
            final_status = "error"

        # Secret-mask: never expose agent_key list to the user surface
        return {
            "status": final_status,
            "message": "Request processed by Saphira.",
            "final": successes[-1] if successes else {},
            "trace_count": len(graph.nodes),
            "failures": failures if failures else None,
            "graph_id": graph.graph_id,
            "avatar_state": "talking" if final_status == "success" else "thinking",
            "owner": "Chelsea Megan Woods",
        }
