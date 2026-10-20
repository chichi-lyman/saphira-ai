"""Async worker supervisor for Saphira's background execution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.core.worker_timeouts import (
    WorkerExecutionTimeout,
    WorkerTimeoutPolicy,
    run_with_watchdog,
    should_abort_loop,
)

from .task import Task, TaskStatus


class AgentWorker(Protocol):
    name: str
    capabilities: set[str]

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None: ...


@dataclass
class ExecutionResult:
    task_id: str
    status: TaskStatus
    artifacts: list[dict[str, Any]]
    errors: list[str]


class TaskExecutor:
    """Executes routed steps while isolating worker failures and enforcing deadlines."""

    def __init__(
        self,
        workers: dict[str, AgentWorker] | None = None,
        timeout_seconds: float = 300,
        soft_timeout_seconds: float = 8,
        max_specialist_hops: int = 10,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if soft_timeout_seconds <= 0:
            raise ValueError("soft_timeout_seconds must be greater than zero")
        self.workers = workers or {}
        self.timeout_seconds = timeout_seconds
        self.soft_timeout_seconds = min(soft_timeout_seconds, timeout_seconds)
        self.max_specialist_hops = max_specialist_hops

    def register(self, worker: AgentWorker) -> None:
        self.workers[worker.name] = worker

    async def run(self, task: Task) -> ExecutionResult:
        if task.autonomy.requires_approval and task.approval_status != "approved":
            task.approval_status = "pending"
            task.set_status(TaskStatus.WAITING_APPROVAL)
            task.emit("approval_required", reason=task.autonomy.reason)
            return ExecutionResult(task.id, task.status, [], [])

        task.set_status(TaskStatus.RUNNING)
        artifacts: list[dict[str, Any]] = []
        errors: list[str] = []
        timeout_policy = WorkerTimeoutPolicy(
            soft_seconds=self.soft_timeout_seconds,
            hard_seconds=self.timeout_seconds,
            max_specialist_hops=self.max_specialist_hops,
        )

        for hop_count, step in enumerate(task.plan):
            if step["status"] == "completed":
                continue
            if should_abort_loop(hop_count, timeout_policy):
                step["status"] = "failed"
                error = (
                    f"specialist hop limit exceeded "
                    f"({timeout_policy.max_specialist_hops})"
                )
                errors.append(error)
                task.emit("step_failed", step=step.get("id"), error=error)
                break

            worker_name = step.get("agent")
            worker = self.workers.get(worker_name) if worker_name else None
            if not worker:
                step["status"] = "skipped"
                task.emit("step_skipped", step=step["id"], reason="worker_not_connected")
                continue
            step["status"] = "running"
            task.emit("step_started", step=step["id"], agent=worker.name)
            try:
                result = await run_with_watchdog(
                    lambda: worker.execute(task, step),
                    policy=timeout_policy,
                    on_soft_timeout=lambda elapsed: task.emit(
                        "step_soft_timeout",
                        step=step["id"],
                        agent=worker.name,
                        elapsed_seconds=round(elapsed, 3),
                    ),
                )
                if result:
                    artifacts.append(result)
                step["status"] = "completed"
                task.emit("step_completed", step=step["id"], agent=worker.name)
            except WorkerExecutionTimeout as exc:
                step["status"] = "failed"
                error = f"{worker.name}: WorkerExecutionTimeout: {exc}"
                errors.append(error)
                task.emit("step_failed", step=step["id"], error=error)
                break
            except Exception as exc:
                step["status"] = "failed"
                error = f"{worker.name}: {type(exc).__name__}: {exc}"
                errors.append(error)
                task.emit("step_failed", step=step["id"], error=error)
                break

        task.artifacts.extend(artifacts)
        task.errors.extend(errors)
        if errors:
            task.set_status(TaskStatus.FAILED)
        elif any(s["status"] == "pending" for s in task.plan):
            task.set_status(TaskStatus.RUNNING)
        else:
            task.set_status(TaskStatus.VERIFYING)
            task.verification = {"passed": True, "checks": ["all_connected_steps_completed"]}
            task.set_status(TaskStatus.COMPLETED)
            task.emit("task_completed", artifact_count=len(artifacts))
        return ExecutionResult(task.id, task.status, artifacts, errors)
