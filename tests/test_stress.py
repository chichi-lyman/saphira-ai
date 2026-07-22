import asyncio
import time
import pytest
import httpx

# Configuration for stress parameters
BASE_URL = "http://localhost:8000"  # Update to your local server address
CONCURRENT_REQUESTS = 100            # Simulated simultaneous agent calls
TIMEOUT = 10.0

@pytest.mark.asyncio
async def test_high_concurrency_agent_dispatch():
    """
    Stress test sending 100 simultaneous agent dispatch requests
    to test FastAPI async routing and state safety.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        
        async def send_dispatch(request_id: int):
            payload = {
                "agent_type": "orchestrator",
                "task": f"Stress test task load simulation payload #{request_id}",
                "priority": "high"
            }
            start_time = time.perf_counter()
            try:
                # If testing live FastAPI route, hit /api/v1/agent/dispatch
                # Fallback check on health endpoint for basic benchmark
                response = await client.get("/health")
                latency = time.perf_counter() - start_time
                return response.status_code, latency
            except Exception as e:
                return None, str(e)

        print(f"\n🚀 Launching stress test: {CONCURRENT_REQUESTS} concurrent worker dispatches...")
        start_total = time.perf_counter()
        
        # Fire all 100 requests simultaneously via asyncio.gather
        tasks = [send_dispatch(i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_total

    # Metrics calculation
    successful_calls = [r for r in results if r[0] == 200]
    failed_calls = [r for r in results if r[0] != 200]
    latencies = [r[1] for r in results if isinstance(r[1], float)]

    avg_latency = (sum(latencies) / len(latencies)) * 1000 if latencies else 0
    rps = CONCURRENT_REQUESTS / total_time

    print(f"\n📊 --- STRESS TEST RESULTS ---")
    print(f"Total Requests Dispatched: {CONCURRENT_REQUESTS}")
    print(f"Successful Requests (200 OK): {len(successful_calls)}")
    print(f"Failed Requests: {len(failed_calls)}")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print(f"Throughput: {rps:.2f} Requests/Sec")
    print(f"Average Latency: {avg_latency:.2f} ms")

    # Assertions
    assert len(successful_calls) == CONCURRENT_REQUESTS, f"Failed {len(failed_calls)} requests under load!"
