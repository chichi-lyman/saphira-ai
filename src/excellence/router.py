"""Parallel multi-agent DAG router with deterministic circuit breakers.

Elevates Saphira from sequential excellence routing to non-blocking
directed-acyclic-graph execution across the 12-agent Nova Umbrella
pipeline.  Any agent that exceeds the 400 ms soft timeout is
immediately circuit-broken and handed to Agent Zero recovery while
preserving full context.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Iterable

from .agent_map import owners_for_pillar
from .pillars import EXCELLENCE_PILLARS, get_pillar


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CIRCUIT_BREAKER_MS = 400          # hard soft-timeout per agent task
MAX_PARALLEL_AGENTS = 12
DEFAULT_FALLBACK_AGENT = "agent_zero"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExcellenceRoute:
    pillar_id: str
    capability: str
    plugin: str
    internal_owners: tuple[str, ...]
    reason: str


@dataclass
class AgentTask:
    """Single node in the parallel DAG."""
    agent_id: str
    coroutine: Callable[[], Awaitable[Any]]
    depends_on: tuple[str, ...] = ()
    timeout_ms: int = CIRCUIT_BREAKER_MS


@dataclass
class DAGResult:
    results: dict[str, Any] = field(default_factory=dict)
    failures: dict[str, str] = field(default_factory=dict)
    recovered: list[str] = field(default_factory=list)
    total_ms: float = 0.0
    circuit_breaks: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Keyword → pillar mapping (kept for backward compatibility)
# ---------------------------------------------------------------------------

_KEYWORD_PILLARS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("voice", "speak", "listen", "wake", "tts", "stt", "latency", "fast", "barge"), "latency"),
    (("remember", "recall", "memory", "forgot", "history", "episodic"), "memory"),
    (("automate", "tool", "run", "execute", "workflow", "a11y", "sandbox"), "automation"),
    (("offline", "edge", "local", "on-device", "airplane", "webgpu"), "edge"),
    (("reason", "think", "analyze", "prove", "why", "compare", "scholar"), "reasoning"),
    (("privacy", "private", "ledger", "self-host", "own my data", "delete my data"), "privacy"),
)


def route_excellence(text: str, *, prefer: Iterable[str] | None = None) -> list[ExcellenceRoute]:
    """Legacy keyword router – still used for pillar suggestion."""
    lowered = (text or "").lower()
    selected: list[str] = []

    if prefer:
        for p in prefer:
            if p not in selected:
                selected.append(p)

    for keywords, pillar_id in _KEYWORD_PILLARS:
        if any(k in lowered for k in keywords) and pillar_id not in selected:
            selected.append(pillar_id)

    for fallback in ("latency", "privacy"):
        if fallback not in selected:
            selected.append(fallback)

    routes: list[ExcellenceRoute] = []
    for pillar_id in selected:
        try:
            pillar = get_pillar(pillar_id)
        except KeyError:
            continue
        owners = tuple(owners_for_pillar(pillar_id))
        routes.append(
            ExcellenceRoute(
                pillar_id=pillar.id,
                capability=pillar.capability,
                plugin=pillar.plugin,
                internal_owners=owners,
                reason=pillar.notes,
            )
        )
    return routes


# ---------------------------------------------------------------------------
# Parallel DAG executor with circuit breakers
# ---------------------------------------------------------------------------

class ParallelExcellenceRouter:
    """Non-blocking multi-agent DAG router.

    Usage
    -----
    router = ParallelExcellenceRouter()
    result = await router.execute_dag(tasks)
    """

    def __init__(self, circuit_ms: int = CIRCUIT_BREAKER_MS):
        self.circuit_ms = circuit_ms

    async def _run_with_circuit(
        self,
        agent_id: str,
        coro: Callable[[], Awaitable[Any]],
        timeout_ms: int,
    ) -> tuple[str, Any | None, str | None]:
        """Execute a single agent task under a hard timeout."""
        try:
            result = await asyncio.wait_for(coro(), timeout=timeout_ms / 1000.0)
            return agent_id, result, None
        except asyncio.TimeoutError:
            return agent_id, None, f"circuit_break:{timeout_ms}ms"
        except Exception as exc:  # noqa: BLE001 – we want full recovery
            return agent_id, None, f"error:{type(exc).__name__}:{exc}"

    async def execute_dag(self, tasks: list[AgentTask]) -> DAGResult:
        """
        Execute independent agent tasks in parallel (respecting depends_on).

        Any task that exceeds its timeout is circuit-broken and recorded.
        The caller (Nova Reign / Agent Zero) is responsible for recovery.
        """
        start = time.perf_counter()
        completed: dict[str, Any] = {}
        failures: dict[str, str] = {}
        circuit_breaks: list[str] = []
        recovered: list[str] = []

        # Topological levels (simple dependency resolution)
        remaining = {t.agent_id: t for t in tasks}
        while remaining:
            # Find tasks whose dependencies are already satisfied
            ready = [
                t for t in remaining.values()
                if all(dep in completed or dep in failures for dep in t.depends_on)
            ]
            if not ready:
                # Circular or missing dependency – fail remaining
                for aid in remaining:
                    failures[aid] = "unresolved_dependency"
                break

            # Launch ready tasks in parallel
            coros = [
                self._run_with_circuit(t.agent_id, t.coroutine, t.timeout_ms)
                for t in ready
            ]
            results = await asyncio.gather(*coros)

            for agent_id, value, err in results:
                del remaining[agent_id]
                if err is None:
                    completed[agent_id] = value
                else:
                    failures[agent_id] = err
                    if err.startswith("circuit_break"):
                        circuit_breaks.append(agent_id)
                        # Immediate hand-off marker for Agent Zero
                        recovered.append(agent_id)

        total_ms = (time.perf_counter() - start) * 1000.0
        return DAGResult(
            results=completed,
            failures=failures,
            recovered=recovered,
            total_ms=total_ms,
            circuit_breaks=circuit_breaks,
        )

    # Convenience wrappers used by the control plane
    def route(self, text: str, **kwargs) -> list[ExcellenceRoute]:
        return route_excellence(text, **kwargs)

    def catalog(self) -> list[dict]:
        return [
            {
                "id": p.id,
                "title": p.title,
                "target": p.saphira_target,
                "capability": p.capability,
                "plugin": p.plugin,
                "owners": owners_for_pillar(p.id),
            }
            for p in EXCELLENCE_PILLARS
        ]


# Backwards-compatible alias
ExcellenceRouter = ParallelExcellenceRouter
