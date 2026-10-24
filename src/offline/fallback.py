"""Offline fallback — route to local Ollama, Whisper.cpp, or vLLM.

Guarantees a native execution path when connectivity drops or the caller
requests low-latency local inference.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx

Backend = Literal["ollama", "vllm", "whisper_cpp", "none"]


@dataclass
class OfflinePlan:
    backend: Backend
    endpoint: str
    reason: str
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class OfflineFallback:
    """Detect and invoke local-only inference backends."""

    def __init__(self) -> None:
        self.ollama_url = os.getenv("SAPHIRA_OLLAMA_URL", "http://127.0.0.1:11434")
        self.vllm_url = os.getenv(
            "SAPHIRA_LOCAL_VLLM_URL", "http://127.0.0.1:8001/v1"
        )
        self.whisper_url = os.getenv(
            "SAPHIRA_WHISPER_CPP_URL", "http://127.0.0.1:8080"
        )

    def plan(self, *,
             force_offline: bool = False,
             need_stt: bool = False,
             prefer_gpu: bool = False) -> OfflinePlan:
        if need_stt:
            return OfflinePlan(
                backend="whisper_cpp",
                endpoint=self.whisper_url,
                reason="speech-to-text requested — whisper.cpp path",
                capabilities=("stt",),
                metadata={"prefer_gpu": prefer_gpu},
            )

        # Prefer Ollama when offline flag set (common local stack)
        if force_offline:
            return OfflinePlan(
                backend="ollama",
                endpoint=f"{self.ollama_url.rstrip('/')}/api/chat",
                reason="force_offline — Ollama local chat",
                capabilities=("chat", "local"),
                metadata={"prefer_gpu": prefer_gpu},
            )

        return OfflinePlan(
            backend="vllm",
            endpoint=f"{self.vllm_url.rstrip('/')}/chat/completions",
            reason="local vLLM OpenAI-compatible path",
            capabilities=("chat", "local", "speculative"),
            metadata={"prefer_gpu": prefer_gpu},
        )

    async def health_probe(self, backend: Backend | None = None) -> dict[str, Any]:
        targets = {
            "ollama": f"{self.ollama_url.rstrip('/')}/api/tags",
            "vllm": f"{self.vllm_url.rstrip('/')}/models",
            "whisper_cpp": self.whisper_url,
        }
        results: dict[str, Any] = {}
        check = [backend] if backend and backend != "none" else list(targets.keys())
        async with httpx.AsyncClient(timeout=httpx.Timeout(2.0, connect=1.0)) as client:
            for name in check:
                url = targets.get(name)  # type: ignore[arg-type]
                if not url:
                    continue
                try:
                    r = await client.get(url)
                    results[name] = {"ok": r.status_code < 500, "status": r.status_code}
                except Exception as exc:
                    results[name] = {"ok": False, "error": str(exc)}
        return results

    async def execute_chat(
        self,
        messages: list[dict[str, str]],
        *,
        force_offline: bool = True,
        model: str | None = None,
    ) -> dict[str, Any]:
        plan = self.plan(force_offline=force_offline)
        model = model or os.getenv("SAPHIRA_LOCAL_MODEL", "llama3.2")

        if plan.backend == "ollama":
            payload = {"model": model, "messages": messages, "stream": False}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(plan.endpoint, json=payload)
                r.raise_for_status()
                data = r.json()
                data["_offline"] = {"backend": plan.backend, "reason": plan.reason}
                return data

        # vLLM / OpenAI-compatible
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(plan.endpoint, json=payload)
            r.raise_for_status()
            data = r.json()
            data["_offline"] = {"backend": plan.backend, "reason": plan.reason}
            return data
