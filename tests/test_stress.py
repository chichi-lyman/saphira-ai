"""High-concurrency dispatch stress test.

Requires a live Saphira API. In CI without a server this test is skipped so the
suite remains green for compile/unit/integration adapters.
"""
from __future__ import annotations

import asyncio
import os
import time

import httpx
import pytest

CONCURRENT_REQUESTS = int(os.getenv("SAPHIRA_STRESS_CONCURRENCY", "100"))
BASE_URL = os.getenv("SAPHIRA_STRESS_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


async def _one(client: httpx.AsyncClient, idx: int) -> tuple[int, float]:
    start = time.perf_counter()
    try:
        r = await client.post(
            f"{BASE_URL}/api/chat",
            json={"messages": [{"role": "user", "content": f"ping-{idx}"}]},
            timeout=10.0,
        )
        return r.status_code, time.perf_counter() - start
    except Exception:
        return 0, time.perf_counter() - start


@pytest.mark.asyncio
async def test_high_concurrency_agent_dispatch():
    # Soft-skip when no live backend is configured for CI
    if os.getenv("SAPHIRA_STRESS_REQUIRE_LIVE", "").lower() not in {"1", "true", "yes"}:
        try:
            async with httpx.AsyncClient() as probe:
                await probe.get(f"{BASE_URL}/health", timeout=1.0)
        except Exception:
            pytest.skip("No live Saphira API at SAPHIRA_STRESS_BASE_URL; set SAPHIRA_STRESS_REQUIRE_LIVE=1 to force")

    async with httpx.AsyncClient() as client:
        start_total = time.perf_counter()
        tasks = [_one(client, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_total

    successful_calls = [r for r in results if r[0] == 200]
    failed_calls = [r for r in results if r[0] != 200]
    latencies = [r[1] for r in results if isinstance(r[1], float)]
    avg_latency = (sum(latencies) / len(latencies)) * 1000 if latencies else 0
    rps = CONCURRENT_REQUESTS / total_time if total_time else 0

    print("\n--- STRESS TEST RESULTS ---")
    print(f"Total Requests Dispatched: {CONCURRENT_REQUESTS}")
    print(f"Successful Requests (200 OK): {len(successful_calls)}")
    print(f"Failed Requests: {len(failed_calls)}")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print(f"Throughput: {rps:.2f} Requests/Sec")
    print(f"Average Latency: {avg_latency:.2f} ms")

    assert len(successful_calls) == CONCURRENT_REQUESTS, (
        f"Failed {len(failed_calls)} requests under load!"
    )
