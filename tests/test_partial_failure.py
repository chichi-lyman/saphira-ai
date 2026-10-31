import pytest
from src.core.partial_failure import TaskRejected, run_independent_tasks

@pytest.mark.asyncio
async def test_one_rejected_subtask_does_not_cancel_successful_siblings():
    async def ok(): return {"answer": 42}
    async def reject(): raise TaskRejected("not authorized for this operation")
    async def broken(): raise RuntimeError("provider unavailable")
    report = await run_independent_tasks({"ok": ok(), "rejected": reject(), "broken": broken()})
    assert report["status"] == "partial"
    assert report["counts"] == {"success": 1, "rejected": 1, "failed": 1}
    assert report["outcomes"][0]["result"] == {"answer": 42}

@pytest.mark.asyncio
async def test_all_success_reports_success():
    async def value(x): return x
    report = await run_independent_tasks({"a": value(1), "b": value(2)})
    assert report["status"] == "success"
    assert report["counts"]["success"] == 2

@pytest.mark.asyncio
async def test_all_failed_reports_failed_without_throwing():
    async def fail(): raise ValueError("bad input")
    report = await run_independent_tasks({"a": fail()})
    assert report["status"] == "failed"
    assert report["outcomes"][0]["error_type"] == "ValueError"
