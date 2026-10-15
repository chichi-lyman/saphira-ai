# © 2026 Chelsea Megan Woods
# Lean stress + latency bench for EliteRouter / TaskGraph / agents.
# Run: python -m benchmarks.bench_elite

from __future__ import annotations
import asyncio
import time
import tracemalloc
import statistics
from typing import List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.task_graph import TaskGraph, Node, Status
from src.core.elite_router import EliteRouter
from src.core.specialist_registry import SpecialistRegistry
from src.memory.nova_aethrea_store import NovaAethreaMemoryStore
from src.core.elite_agent_base import EliteAgentBase


class _FastAgent(EliteAgentBase):
    name = "fast"
    async def process(self, payload):
        return {"status": "success", "message": "ok"}


def _registry():
    reg = SpecialistRegistry()
    mem = NovaAethreaMemoryStore()
    agent = _FastAgent(mem)
    from src.core.specialist_registry import CAPABILITY_MAP
    for key in set(CAPABILITY_MAP.values()):
        reg.register(key, agent)
    return reg, mem


async def bench_route_latency(n: int = 500) -> dict:
    reg, _ = _registry()
    router = EliteRouter(reg, max_parallel=4)
    times: List[float] = []
    for _ in range(n):
        t0 = time.perf_counter()
        await router.route("bench")
        times.append((time.perf_counter() - t0) * 1e6)  # µs
    times.sort()
    return {
        "n": n,
        "p50_us": round(times[len(times)//2], 1),
        "p95_us": round(times[int(len(times)*0.95)], 1),
        "p99_us": round(times[int(len(times)*0.99)], 1),
        "mean_us": round(statistics.mean(times), 1),
        "min_us": round(times[0], 1),
        "router_metrics": router.metrics,
    }


async def bench_concurrent(rps_target: int = 200, duration_s: float = 1.0) -> dict:
    reg, _ = _registry()
    router = EliteRouter(reg, max_parallel=8)
    ok = fail = 0
    latencies: List[float] = []
    t_end = time.perf_counter() + duration_s

    async def one():
        nonlocal ok, fail
        t0 = time.perf_counter()
        try:
            r = await router.route("concurrent")
            latencies.append((time.perf_counter() - t0) * 1000)
            if r.get("status") in ("success", "partial"):
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1

    tasks = []
    while time.perf_counter() < t_end:
        tasks.append(asyncio.create_task(one()))
        if len(tasks) >= rps_target * 2:
            await asyncio.sleep(0)
        await asyncio.sleep(0)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = duration_s
    achieved = (ok + fail) / elapsed if elapsed else 0
    return {
        "ok": ok,
        "fail": fail,
        "achieved_rps": round(achieved, 1),
        "p50_ms": round(statistics.median(latencies), 2) if latencies else None,
        "p95_ms": round(sorted(latencies)[int(len(latencies)*0.95)], 2) if latencies else None,
    }


async def bench_self_heal() -> dict:
    class Boom(EliteAgentBase):
        name = "boom"
        async def process(self, payload):
            raise RuntimeError("inject")

    agent = Boom()
    t0 = time.perf_counter()
    r = await agent.safe_run({"text": "x"})
    ms = (time.perf_counter() - t0) * 1000
    return {
        "status": r.get("status"),
        "recover_ms": round(ms, 2),
        "attempts": r.get("attempt"),
    }


def bench_memory_footprint() -> dict:
    tracemalloc.start()
    reg, mem = _registry()
    router = EliteRouter(reg)
    g = TaskGraph("footprint")
    for i in range(20):
        g.add(Node(id=str(i), capability="intent.parse", agent_key="saphira", payload={}))
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "current_mb": round(current / 1e6, 3),
        "peak_mb": round(peak / 1e6, 3),
        "records": mem.metrics(),
    }


async def main():
    print("=== Saphira Elite Bench ===")
    lat = await bench_route_latency(300)
    print("route_latency_us:", lat)
    conc = await bench_concurrent(500, 1.0)
    print("concurrent:", conc)
    heal = await bench_self_heal()
    print("self_heal:", heal)
    mem = bench_memory_footprint()
    print("memory_mb:", mem)
    print("OK")


if __name__ == "__main__":
    asyncio.run(main())
