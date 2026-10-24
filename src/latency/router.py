"""Latency router — prefer local WebGPU / vLLM speculative paths.

Design target: 180–350ms TTS/STT/TTFT on device; sub-second text TTFT when
local vLLM is warm. Cloud is fallback, not the default when local is ready.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Literal

ExecutionPath = Literal["local_vllm", "local_webgpu", "cloud", "offline_stub"]


@dataclass
class LatencyDecision:
    path: ExecutionPath
    reason: str
    prefer_gpu: bool
    estimated_ttft_ms: int
    metadata: dict[str, Any] = field(default_factory=dict)


class LatencyRouter:
    """Chooses the lowest-latency executable path for a task."""

    def __init__(self) -> None:
        self.local_vllm_url = os.getenv(
            "SAPHIRA_LOCAL_VLLM_URL", "http://127.0.0.1:8001/v1"
        )
        self.webgpu_enabled = os.getenv("SAPHIRA_WEBGPU", "0") == "1"
        self.force_local = os.getenv("SAPHIRA_FORCE_LOCAL", "0") == "1"

    def decide(
        self,
        *,
        task: str = "",
        prefer_gpu: bool = False,
        offline: bool = False,
        local_vllm_healthy: bool | None = None,
    ) -> LatencyDecision:
        started = time.perf_counter()
        prefer_gpu = prefer_gpu or "gpu" in (task or "").lower()

        if offline:
            return LatencyDecision(
                path="offline_stub" if local_vllm_healthy is False else "local_vllm",
                reason="offline mode — local only",
                prefer_gpu=prefer_gpu,
                estimated_ttft_ms=220 if prefer_gpu else 320,
                metadata={"elapsed_decide_ms": _ms(started)},
            )

        if self.force_local or local_vllm_healthy is True:
            return LatencyDecision(
                path="local_vllm",
                reason="local vLLM preferred (force_local or healthy)",
                prefer_gpu=prefer_gpu,
                estimated_ttft_ms=180 if prefer_gpu else 280,
                metadata={
                    "endpoint": self.local_vllm_url,
                    "speculative_decoding": True,
                    "elapsed_decide_ms": _ms(started),
                },
            )

        if prefer_gpu and self.webgpu_enabled:
            return LatencyDecision(
                path="local_webgpu",
                reason="WebGPU acceleration requested and enabled",
                prefer_gpu=True,
                estimated_ttft_ms=200,
                metadata={"elapsed_decide_ms": _ms(started)},
            )

        # Default: cloud with local standby metadata
        return LatencyDecision(
            path="cloud",
            reason="cloud default; local standby available",
            prefer_gpu=prefer_gpu,
            estimated_ttft_ms=400,
            metadata={
                "local_standby": self.local_vllm_url,
                "elapsed_decide_ms": _ms(started),
            },
        )


def _ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
