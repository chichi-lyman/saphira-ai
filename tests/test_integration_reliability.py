import asyncio
import pytest

from src.integrations.reliability import invoke_provider, invoke_providers


@pytest.mark.asyncio
async def test_provider_rejection_isolated_from_healthy_provider():
    async def healthy():
        return {"status": "ok"}
    async def rejected():
        raise ConnectionError("provider unavailable")
    results = await invoke_providers([("healthy", healthy), ("missing", rejected)])
    assert results[0].ok and results[0].value == {"status": "ok"}
    assert not results[1].ok and "provider unavailable" in results[1].error


@pytest.mark.asyncio
async def test_provider_timeout_becomes_failed_result():
    async def slow():
        await asyncio.sleep(0.05)
    result = await invoke_provider("slow", slow, timeout_seconds=0.001)
    assert not result.ok and "TimeoutError" in result.error
