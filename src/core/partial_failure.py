"""Independent subtask execution with partial-success semantics.

Each task outcome is isolated. One rejection or exception does not cancel
other independent tasks. Cancellation remains cooperative and is re-raised.
"""
from __future__ import annotations
import asyncio
from dataclasses import asdict, dataclass
from typing import Any, Awaitable, Mapping

@dataclass(frozen=True)
class TaskOutcome:
    task_id: str
    status: str  # success | rejected | failed
    result: Any = None
    error_type: str | None = None
    message: str | None = None

class TaskRejected(Exception):
    """Expected task-level rejection that must not cancel sibling tasks."""

async def run_independent_tasks(tasks: Mapping[str, Awaitable[Any]]) -> dict[str, Any]:
    """Run independent awaitables concurrently and return partial results."""
    async def capture(task_id: str, awaitable: Awaitable[Any]) -> TaskOutcome:
        try:
            return TaskOutcome(task_id=task_id, status="success", result=await awaitable)
        except asyncio.CancelledError:
            raise
        except TaskRejected as exc:
            return TaskOutcome(task_id=task_id, status="rejected", error_type=type(exc).__name__, message=str(exc)[:500])
        except Exception as exc:
            return TaskOutcome(task_id=task_id, status="failed", error_type=type(exc).__name__, message="Subtask failed; sibling tasks continued")
    outcomes = await asyncio.gather(*(capture(key, value) for key, value in tasks.items()))
    counts = {"success": 0, "rejected": 0, "failed": 0}
    for outcome in outcomes: counts[outcome.status] += 1
    status = "success" if counts["failed"] == 0 and counts["rejected"] == 0 else ("partial" if counts["success"] else "failed")
    return {"status": status, "total": len(outcomes), "counts": counts, "outcomes": [asdict(item) for item in outcomes]}
