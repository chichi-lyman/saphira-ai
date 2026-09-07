"""Immutable execution context used for memory and authorization scoping."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionContext:
    tenant_id: str
    user_id: str
    conversation_id: str
    task_id: str
    execution_id: str
    device_id: str | None = None
    parent_execution_id: str | None = None

    def validate(self) -> None:
        required = {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "task_id": self.task_id,
            "execution_id": self.execution_id,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("missing_execution_context:" + ",".join(missing))

    def memory_scope(self) -> tuple[str, str, str, str, str]:
        self.validate()
        return (
            self.tenant_id,
            self.user_id,
            self.conversation_id,
            self.task_id,
            self.execution_id,
        )
