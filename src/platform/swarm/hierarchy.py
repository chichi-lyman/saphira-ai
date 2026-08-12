"""Hierarchical swarm with budget/time limits."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

AgentFn = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]

@dataclass
class SwarmBudget:
    max_agents: int = 5
    max_seconds: float = 30.0
    max_tokens_estimate: int = 50_000

@dataclass
class SwarmResult:
    status: str
    lead: str
    agents_run: List[str]
    outputs: Dict[str, Any]
    elapsed_seconds: float
    truncated: bool = False

class HierarchicalSwarm:
    def __init__(self, lead: str, specialists: Dict[str, AgentFn], budget: Optional[SwarmBudget] = None):
        self.lead = lead
        self.specialists = specialists
        self.budget = budget or SwarmBudget()

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> SwarmResult:
        context = dict(context or {})
        context["task"] = task
        start = time.perf_counter()
        names = list(self.specialists.keys())[: self.budget.max_agents]
        outputs: Dict[str, Any] = {}
        truncated = False

        async def _run_one(name: str) -> None:
            nonlocal truncated
            if time.perf_counter() - start > self.budget.max_seconds:
                truncated = True
                outputs[name] = {"status": "skipped", "reason": "budget_time"}
                return
            try:
                outputs[name] = await asyncio.wait_for(self.specialists[name](context), timeout=max(0.1, self.budget.max_seconds - (time.perf_counter() - start)))
            except Exception as e:
                outputs[name] = {"status": "error", "error": str(e)}

        await asyncio.gather(*[_run_one(n) for n in names])
        return SwarmResult(status="success", lead=self.lead, agents_run=names, outputs=outputs, elapsed_seconds=time.perf_counter() - start, truncated=truncated)
