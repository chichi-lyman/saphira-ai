"""Live excellence telemetry — latency and memory/routing stats.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from src.memory.ledger import dual_memory


@dataclass
class ExcellenceTelemetry:
    """In-process ring buffers for live benchmark-style stats."""

    max_samples: int = 200
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _dispatch_ms: deque = field(default_factory=lambda: deque(maxlen=200))
    _latency_paths: dict = field(default_factory=dict)
    _agent_hits: dict = field(default_factory=dict)
    _pillar_hits: dict = field(default_factory=dict)
    _started_at: float = field(default_factory=time.time)

    def record_dispatch(
        self,
        *,
        agent: str,
        latency_path: str,
        elapsed_ms: int,
        pillars: list[str] | None = None,
    ) -> None:
        with self._lock:
            self._dispatch_ms.append(elapsed_ms)
            self._latency_paths[latency_path] = self._latency_paths.get(latency_path, 0) + 1
            self._agent_hits[agent] = self._agent_hits.get(agent, 0) + 1
            for p in pillars or []:
                self._pillar_hits[p] = self._pillar_hits.get(p, 0) + 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            samples = list(self._dispatch_ms)
            paths = dict(self._latency_paths)
            agents = dict(self._agent_hits)
            pillars = dict(self._pillar_hits)

        avg = int(sum(samples) / len(samples)) if samples else None
        p95 = None
        if samples:
            ordered = sorted(samples)
            p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]

        mem = dual_memory.memory_check()
        return {
            "status": "ok",
            "uptime_sec": int(time.time() - self._started_at),
            "latency": {
                "samples": len(samples),
                "avg_dispatch_ms": avg,
                "p95_dispatch_ms": p95,
                "target_ttft_ms": "180-350",
                "paths": paths,
            },
            "memory": {
                "ram_entries": mem.get("ram_entries"),
                "durable_backend": mem.get("durable_backend"),
                "pgvector_configured": mem.get("pgvector_configured"),
                "recall_design_target": "98.2%",
            },
            "routing": {
                "agent_hits": agents,
                "pillar_hits": pillars,
            },
            "surface_agent": "Saphira",
        }


excellence_telemetry = ExcellenceTelemetry()
