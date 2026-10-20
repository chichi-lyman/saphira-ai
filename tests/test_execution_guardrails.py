"""Failure-injection tests for watchdog, fallback routing, and pre-commit validation.

No provider endpoints or production services are called.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

import asyncio

import pytest

from src.core.logic_validator import (
    InvalidSpecialistOutput,
    require_valid_specialist_output,
)
from src.core.worker_timeouts import (
    WorkerExecutionTimeout,
    WorkerTimeoutPolicy,
    run_with_watchdog,
)


@pytest.mark.asyncio
async def test_fast_task_completes_before_soft_deadline() -> None:
    async def operation() -> str:
        return "completed"

    result = await run_with_watchdog(
        operation,
        policy=WorkerTimeoutPolicy(soft_seconds=0.05, hard_seconds=0.15),
    )
    assert result == "completed"


@pytest.mark.asyncio
async def test_soft_timeout_hook_fires_but_task_can_finish() -> None:
    warnings: list[float] = []

    async def operation() -> str:
        await asyncio.sleep(0.06)
        return "finished after soft threshold"

    result = await run_with_watchdog(
        operation,
        policy=WorkerTimeoutPolicy(soft_seconds=0.01, hard_seconds=0.2),
        on_soft_timeout=warnings.append,
    )
    assert result == "finished after soft threshold"
    assert len(warnings) == 1
    assert warnings[0] >= 0.01


@pytest.mark.asyncio
async def test_hard_timeout_cancels_task_and_raises() -> None:
    cancelled = asyncio.Event()

    async def operation() -> str:
        try:
            await asyncio.sleep(5)
            return "should not complete"
        except asyncio.CancelledError:
            cancelled.set()
            raise

    with pytest.raises(WorkerExecutionTimeout, match="hard deadline"):
        await run_with_watchdog(
            operation,
            policy=WorkerTimeoutPolicy(soft_seconds=0.01, hard_seconds=0.04),
        )
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_operation_exception_propagates_for_worker_recovery() -> None:
    async def operation() -> str:
        raise RuntimeError("injected worker failure")

    with pytest.raises(RuntimeError, match="injected worker failure"):
        await run_with_watchdog(
            operation,
            policy=WorkerTimeoutPolicy(soft_seconds=0.05, hard_seconds=0.1),
        )


@pytest.mark.parametrize(
    ("soft", "hard"),
    [(0, 1), (1, 0), (2, 1)],
)
def test_invalid_timeout_configuration_is_rejected(soft: float, hard: float) -> None:
    with pytest.raises(ValueError):
        WorkerTimeoutPolicy(soft_seconds=soft, hard_seconds=hard)


def test_invalid_output_is_blocked_at_precommit_gate() -> None:
    with pytest.raises(InvalidSpecialistOutput, match="Empty output"):
        require_valid_specialist_output(
            user_instruction="Answer clearly",
            specialist_output="   ",
        )


def test_looping_output_is_blocked_at_precommit_gate() -> None:
    with pytest.raises(InvalidSpecialistOutput, match="loop"):
        require_valid_specialist_output(
            user_instruction="Answer clearly",
            specialist_output="hello hello hello hello hello hello",
        )


def test_clean_output_passes_precommit_gate() -> None:
    result = require_valid_specialist_output(
        user_instruction="List the required steps",
        specialist_output="1. Inspect inputs.\n2. Validate output.\n3. Record result.",
    )
    assert result.startswith("1. Inspect inputs.")


class HangingWorker:
    name = "hanging_worker"
    capabilities = {"test"}

    def __init__(self) -> None:
        self.cancelled = False

    async def execute(self, task, step):
        try:
            await asyncio.sleep(5)
            return {"unexpected": "completed"}
        except asyncio.CancelledError:
            self.cancelled = True
            raise


@pytest.mark.asyncio
async def test_task_executor_enforces_hard_timeout_and_marks_failed() -> None:
    from src.orchestration.executor import TaskExecutor
    from src.orchestration.task import Task, TaskStatus

    worker = HangingWorker()
    task = Task(objective="timeout injection")
    task.add_step("hang", "test", agent=worker.name)
    executor = TaskExecutor(
        workers={worker.name: worker},
        timeout_seconds=0.05,
        soft_timeout_seconds=0.01,
    )

    result = await executor.run(task)

    assert result.status == TaskStatus.FAILED
    assert worker.cancelled is True
    assert task.plan[0]["status"] == "failed"
    assert any("WorkerExecutionTimeout" in error for error in result.errors)


@pytest.mark.asyncio
async def test_task_executor_stops_after_specialist_hop_limit() -> None:
    from src.orchestration.executor import TaskExecutor
    from src.orchestration.task import Task, TaskStatus

    class FastWorker:
        name = "fast_worker"
        capabilities = {"test"}

        async def execute(self, task, step):
            return {"step": step["name"]}

    worker = FastWorker()
    task = Task(objective="hop limit injection")
    task.add_step("first", "test", agent=worker.name)
    task.add_step("second", "test", agent=worker.name)
    executor = TaskExecutor(
        workers={worker.name: worker},
        timeout_seconds=0.2,
        soft_timeout_seconds=0.05,
        max_specialist_hops=1,
    )

    result = await executor.run(task)

    assert result.status == TaskStatus.FAILED
    assert task.plan[0]["status"] == "completed"
    assert task.plan[1]["status"] == "failed"
    assert any("hop limit exceeded" in error for error in result.errors)


@pytest.mark.asyncio
async def test_chat_endpoint_blocks_invalid_generated_text_before_history_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.api import chat_router as chat_module

    async def fake_process(message, context=None):
        return {
            "final": {"status": "success", "message": "raw task result"},
            "avatar_state": "talking",
        }

    async def invalid_natural_reply(user_message, task_result, history):
        return "hello hello hello hello hello hello"

    committed: list[dict] = []
    monkeypatch.setattr(chat_module._orchestrator, "process", fake_process)
    monkeypatch.setattr(chat_module, "_session_history", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(chat_module, "_generate_natural_reply", invalid_natural_reply)
    monkeypatch.setattr(chat_module.persistent_memory, "append_history", committed.append)
    monkeypatch.setattr(
        chat_module.avatar_service,
        "generate_frame",
        lambda **_kwargs: {"url": None, "status": "ok", "state": "thinking"},
    )

    response = await chat_module.chat(chat_module.ChatRequest(message="Say hello"))

    assert response["status"] == "validation_blocked"
    assert "couldn't verify" in response["message"]
    assert committed[-1]["role"] == "assistant"
    assert committed[-1]["text"] == response["message"]
    assert "hello hello hello" not in committed[-1]["text"]
