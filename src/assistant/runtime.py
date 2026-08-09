"""Production composition root for the Saphira executive runtime."""
from __future__ import annotations

from src.assistant.executive import SaphiraExecutive
from src.orchestration.executor import AgentWorker


def build_saphira(workers: list[AgentWorker] | None = None) -> SaphiraExecutive:
    """Build one Saphira instance and register background workers."""
    assistant = SaphiraExecutive()
    for worker in workers or []:
        assistant.executor.register(worker)
    return assistant
