"""Provider-neutral contracts for multimodal and real-world Saphira adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolScope:
    name: str
    description: str
    autonomy_level: int
    side_effect: bool = False
    requires_approval: bool = False


@dataclass
class ToolInvocation:
    capability: str
    arguments: dict[str, Any] = field(default_factory=dict)
    approved: bool = False
    actor: str = "saphira"


@dataclass
class AdapterResult:
    success: bool
    data: Any = None
    error: str | None = None
    audit: dict[str, Any] = field(default_factory=dict)


class SpeechAdapter(Protocol):
    async def transcribe(self, audio: bytes, *, sample_rate: int = 16000) -> str: ...
    async def synthesize(self, text: str, *, voice: str | None = None) -> bytes: ...


class VisionAdapter(Protocol):
    async def analyze(self, payload: bytes, *, mime_type: str) -> dict[str, Any]: ...


class WebGroundingAdapter(Protocol):
    async def search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]: ...


class SystemAdapter(Protocol):
    async def invoke(self, call: ToolInvocation) -> AdapterResult: ...


class SmartEnvironmentAdapter(Protocol):
    async def invoke(self, call: ToolInvocation) -> AdapterResult: ...


class SandboxAdapter(Protocol):
    async def execute(self, code: str, *, timeout_seconds: int = 30) -> AdapterResult: ...


class CadAdapter(Protocol):
    async def generate(self, specification: str, *, format: str = "openscad") -> AdapterResult: ...


class MemoryAdapter(Protocol):
    async def recall(self, query: str, *, limit: int = 8) -> list[dict[str, Any]]: ...
    async def remember(self, record: dict[str, Any]) -> None: ...


class ProactiveScheduler(Protocol):
    async def schedule(self, trigger: dict[str, Any], task: dict[str, Any]) -> str: ...
    async def cancel(self, schedule_id: str) -> bool: ...
