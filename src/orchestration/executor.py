"""Background execution contract for Saphira's worker agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .task import Task, TaskStatus


class AgentWorker(Protocol):
    name: str
    capabilities: set[str]

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class ExecutionResult:
    task_id: str
    status: TaskStatus
    artifacts: list[dict[str, Any]]
    errors: list[str]


class TaskExecutor:
    """Executes a task graph through registered workers.

    The executor is intentionally framework-agnostic so it can later be
    backed by asyncio, Celery, a queue service, or a distributed worker pool.
    """

    def __init__(self, workers: dict[str, AgentWorker] | None = None) -> None:
        self.workers = workers or {}

    async def run(self, task: Task) -> ExecutionResult:
        task.status = TaskStatus.RUNNING
        artifacts: list[dict[str, Any]] = []
        errors: list[str] = []

        for step in task.plan:
            worker_name = next(
                (name for name, worker in self.workers.items()
                 if step["capability"] in worker.capabilities),
                None,
            )
            if not worker_name:
                # Planning-only deployments may not have every worker wired yet.
                continue
            try:
                result = await self.workers[worker_name].execute(task, step)
                if result:
                    artifacts.append(result)
            except Exception as exc:  # worker boundary: isolate one failure
                errors.append(f"{worker_name}: {exc}")

        task.artifacts.extend(artifacts)
        task.errors.extend(errors)
        task.status = TaskStatus.FAILED if errors else TaskStatus.COMPLETED
        return ExecutionResult(task.id, task.status, artifacts, errors)
