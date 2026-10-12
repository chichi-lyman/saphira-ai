# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time
import uuid


class ProviderName(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    XAI = "xai"


@dataclass(frozen=True)
class GenerateRequest:
    prompt: str
    system: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerateResult:
    status: str  # success | error | disabled | not_configured
    text: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    message: Optional[str] = None
    usage: Optional[dict[str, int]] = None
    latency_ms: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    raw: Optional[dict[str, Any]] = None


@dataclass
class InvocationRecord:
    """Append-only telemetry for every model call (success or failure)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ts: float = field(default_factory=time.time)
    provider: str = ""
    model: str = ""
    status: str = ""
    latency_ms: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
