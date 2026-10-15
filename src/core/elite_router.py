# © 2026 Chelsea Megan Woods
# Lean EliteRouter — capability route, cycle guard, bounded parallel, latency metrics.

from __future__ import annotations
from typing import Any, Dict, List, Optional
import asyncio
import time
import uuid
import logging

from src.core.task_graph import TaskGraph, Node, Status

logger = logging.getLogger("router")

class EliteRouter:
    __slots__ = ("registry", "core", "max_parallel", "max_depth", "calls", "total_ms")

    def __init__(self, registry, core=None, max_parallel: int = 4, max_depth: int = 10):
        self.registry = registry
        self.core = core
        self.max_parallel = max_parallel
        self.max_depth = max_depth
        self.calls = 0
        self.total_ms = 0.0

    @property
    def metrics(self) -> Dict[str, Any]:
        avg = self.total_ms / self.calls if self.calls else 0.0
        return {"calls": self.calls, "avg_ms": round(avg, 2), "total_ms": round(self.total_ms, 2)}

    async def route(self, user_input: str, context: Optional[Dict] = None, tenant_id: str = "default") -> Dict[str, Any]:
        t0 = time.perf_counter()
        self.calls += 1
        ctx = context or {}
        g = TaskGraph(user_input, tenant_id)

        plan = self._plan(user_input)
        if not plan:
            if self.core:
                return await self.core.process(user_input, ctx)
            return {"status": "error", "message": "no plan"}

        prev = None
        for step in plan:
            nid = str(uuid.uuid4())
            g.add(Node(
                id=nid,
                capability=step["c"],
                agent_key=self.registry.agent_for(step["c"]),
                payload={**ctx, "user_input": user_input, "tenant_id": tenant_id},
                depends_on=[prev] if prev and step.get("seq", True) else [],
            ))
            prev = nid

        if g.has_cycle():
            return {"status": "error", "message": "cycle blocked"}

        sem = asyncio.Semaphore(self.max_parallel)
        depth = 0
        while depth < self.max_depth:
            ready = g.ready()
            if not ready:
                break
            depth += 1

            async def run(n: Node):
                async with sem:
                    return await self._exec(n, g)

            results = await asyncio.gather(*(run(n) for n in ready), return_exceptions=True)
            for n, res in zip(ready, results):
                if isinstance(res, Exception):
                    g.mark_fail(n.id, str(res))
                elif isinstance(res, dict) and res.get("status") in ("success", "recovered_from_failure", "scene_executed"):
                    g.mark_ok(n.id, res)
                else:
                    g.mark_fail(n.id, (res or {}).get("message", "fail") if isinstance(res, dict) else "fail")

            if g.failed and not g.ready():
                break

        ms = (time.perf_counter() - t0) * 1000
        self.total_ms += ms
        return self._synth(g, ms)

    async def _exec(self, n: Node, g: TaskGraph) -> Dict[str, Any]:
        agent = self.registry.get(n.agent_key)
        if not agent:
            return {"status": "error", "message": f"no agent {n.capability}"}
        n.status = Status.RUN
        n.t0 = time.perf_counter()
        env = {**n.payload, "isolation_token": n.isolation_token, "capability": n.capability, "tenant_id": g.tenant}
        try:
            if hasattr(agent, "safe_run"):
                return await asyncio.wait_for(agent.safe_run(env), n.timeout_s)
            return await asyncio.wait_for(agent.process(env), n.timeout_s)
        except asyncio.TimeoutError:
            return {"status": "error", "message": "timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _plan(self, text: str) -> List[Dict]:
        # fixed pipeline default — deterministic, zero LLM cost for routing
        return [
            {"c": "intent.parse", "seq": True},
            {"c": "perception.entity", "seq": True},
            {"c": "security.gate", "seq": True},
            {"c": "governance.plan", "seq": True},
            {"c": "memory.read", "seq": True},
            {"c": "device.execute", "seq": True},
        ]

    def _synth(self, g: TaskGraph, ms: float) -> Dict[str, Any]:
        oks = [n.result for n in g.nodes.values() if n.status == Status.OK and n.result]
        fails = [{"a": n.agent_key, "e": n.error} for n in g.nodes.values() if n.status == Status.FAIL]
        status = "success" if oks and not fails else ("partial" if oks else "error")
        return {
            "status": status,
            "message": "ok",
            "final": oks[-1] if oks else {},
            "nodes": len(g.nodes),
            "fails": fails or None,
            "latency_ms": round(ms, 2),
            "graph_id": g.graph_id,
            "owner": "Chelsea Megan Woods",
        }
