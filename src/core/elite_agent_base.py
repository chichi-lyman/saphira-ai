# © 2026 Chelsea Megan Woods
# Lean EliteAgentBase — isolation, self-heal, metrics. No wrappers beyond necessity.

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio
import time
import uuid
import logging

logger = logging.getLogger("elite")

class EliteAgentBase(ABC):
    name: str = "base"
    capabilities: list = []
    default_policy: str = "ALLOW"
    max_timeout_s: float = 30.0
    max_retries: int = 2
    SYSTEM_VOICE: str = ""

    def __init__(self, memory_store=None):
        self.memory = memory_store
        self._calls = 0
        self._total_ms = 0.0
        self._failures = 0

    @property
    def metrics(self) -> Dict[str, Any]:
        avg = self._total_ms / self._calls if self._calls else 0.0
        return {
            "agent": self.name,
            "calls": self._calls,
            "failures": self._failures,
            "avg_ms": round(avg, 2),
            "total_ms": round(self._total_ms, 2),
        }

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()
        isolation = payload.get("isolation_token") or str(uuid.uuid4())
        tenant = payload.get("tenant_id", "default")
        self._calls += 1

        # cheap memory pull (optional)
        mem = []
        if self.memory is not None:
            try:
                q = payload.get("text") or payload.get("objective") or ""
                mem = await self.memory.recall(tenant, q, top_k=4)
            except Exception:
                pass

        enriched = {**payload, "isolation_token": isolation, "memory_context": mem}
        last_err = None
        for attempt in range(1, self.max_retries + 2):
            try:
                out = await asyncio.wait_for(self.process(enriched), self.max_timeout_s)
                out.setdefault("agent", self.name)
                out.setdefault("status", "success")
                out["isolation_token"] = isolation
                out["attempt"] = attempt
                out["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
                self._total_ms += out["latency_ms"]
                if self.memory is not None and out.get("status") == "success":
                    try:
                        await self.memory.write_outcome(tenant, self.name, out)
                    except Exception:
                        pass
                return out
            except asyncio.TimeoutError:
                last_err = "timeout"
            except Exception as e:
                last_err = str(e)
                logger.exception("%s fail attempt %d", self.name, attempt)

        self._failures += 1
        ms = round((time.perf_counter() - t0) * 1000, 2)
        self._total_ms += ms
        return {
            "agent": self.name,
            "status": "recovered_from_failure",
            "error": last_err,
            "isolation_token": isolation,
            "latency_ms": ms,
        }

    @abstractmethod
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...
