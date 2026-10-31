"""Concurrent HTTP smoke/load probe for a deployed Saphira endpoint.

Example:
  python scripts/load_test_saphira.py --url https://api.example.com/api/integrations/automation/health --requests 200 --concurrency 20
"""
from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    if args.requests < 1 or args.concurrency < 1:
        parser.error("--requests and --concurrency must be positive")

    semaphore = asyncio.Semaphore(args.concurrency)
    latencies: list[float] = []
    failures = 0

    async with httpx.AsyncClient(timeout=args.timeout) as client:
        async def one() -> None:
            nonlocal failures
            async with semaphore:
                started = time.perf_counter()
                try:
                    response = await client.get(args.url)
                    if response.status_code >= 400:
                        failures += 1
                except httpx.HTTPError:
                    failures += 1
                finally:
                    latencies.append((time.perf_counter() - started) * 1000)

        started_all = time.perf_counter()
        await asyncio.gather(*(one() for _ in range(args.requests)))
        elapsed = time.perf_counter() - started_all

    ordered = sorted(latencies)
    def percentile(p: float) -> float:
        return round(ordered[min(len(ordered) - 1, int((len(ordered) - 1) * p))], 2)

    print({
        "requests": args.requests,
        "concurrency": args.concurrency,
        "failures": failures,
        "error_rate": round(failures / args.requests, 4),
        "throughput_rps": round(args.requests / elapsed, 2),
        "latency_ms_p50": percentile(0.50),
        "latency_ms_p95": percentile(0.95),
        "latency_ms_max": round(max(ordered), 2),
    })


if __name__ == "__main__":
    asyncio.run(main())
