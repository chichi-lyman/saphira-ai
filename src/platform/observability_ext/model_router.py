"""Model routing fabric by task class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ModelRoute:
    task_class: str
    provider: str
    model: str
    max_latency_ms: int
    cost_tier: str

DEFAULT_ROUTES: Dict[str, ModelRoute] = {
    "chat": ModelRoute("chat", "gemini", "gemini-flash", 1500, "low"),
    "reason": ModelRoute("reason", "openai", "gpt-4.1", 8000, "high"),
    "code": ModelRoute("code", "openai", "gpt-4.1", 10000, "high"),
    "embed": ModelRoute("embed", "local", "minilm", 200, "low"),
    "tts": ModelRoute("tts", "elevenlabs", "multilingual_v2", 3000, "medium"),
}

class ModelRouter:
    def __init__(self, routes: Optional[Dict[str, ModelRoute]] = None):
        self.routes = dict(routes or DEFAULT_ROUTES)
    def resolve(self, task_class: str) -> ModelRoute:
        return self.routes.get(task_class, self.routes["chat"])

model_router = ModelRouter()
