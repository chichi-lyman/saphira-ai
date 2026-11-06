# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""Evaluation runner — executes registered benchmarks against any agent callable.

Usage pattern (internal):
    runner = EvaluationRunner(model_fn=my_agent_call)
    result = await runner.run("mmlu", n_shots=0, subjects=["astronomy"], limit=50)
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .registry import get_registry

logger = logging.getLogger("Saphira.Evaluation.Runner")

# model_fn signature: async (prompt: str, **kwargs) -> str
ModelFn = Callable[..., Union[str, Awaitable[str]]]


@dataclass
class EvaluationResult:
    benchmark: str
    overall_score: float  # 0.0 – 1.0
    n_correct: int
    n_total: int
    n_shots: int
    subjects: List[str]
    per_subject: Dict[str, float] = field(default_factory=dict)
    latency_ms: float = 0.0
    details: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    owner_agents: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark": self.benchmark,
            "overall_score": round(self.overall_score, 4),
            "n_correct": self.n_correct,
            "n_total": self.n_total,
            "n_shots": self.n_shots,
            "subjects": self.subjects,
            "per_subject": {k: round(v, 4) for k, v in self.per_subject.items()},
            "latency_ms": round(self.latency_ms, 1),
            "owner_agents": self.owner_agents,
            "metadata": self.metadata,
        }


class EvaluationRunner:
    """Orchestrates standardized benchmark runs for any Saphira agent surface."""

    def __init__(
        self,
        model_fn: ModelFn,
        *,
        agent_name: str = "saphira",
        record_details: bool = True,
    ) -> None:
        self.model_fn = model_fn
        self.agent_name = agent_name
        self.record_details = record_details
        self.registry = get_registry()

    async def run(
        self,
        benchmark_key: str = "mmlu",
        *,
        n_shots: int = 0,
        subjects: Optional[List[str]] = None,
        limit: Optional[int] = None,
        seed: int = 42,
        **kwargs: Any,
    ) -> EvaluationResult:
        """Run a registered benchmark and return a structured EvaluationResult."""
        cls = self.registry.get(benchmark_key)
        if cls is None:
            raise ValueError(
                f"Unknown benchmark '{benchmark_key}'. "
                f"Registered: {self.registry.list_keys()}"
            )

        meta = self.registry.metadata(benchmark_key) or {}
        bench = cls(
            n_shots=n_shots,
            subjects=subjects,
            limit=limit,
            seed=seed,
            **kwargs,
        )

        t0 = time.perf_counter()
        raw = await bench.evaluate(self.model_fn, record_details=self.record_details)
        elapsed = (time.perf_counter() - t0) * 1000.0

        result = EvaluationResult(
            benchmark=benchmark_key,
            overall_score=raw["overall_score"],
            n_correct=raw["n_correct"],
            n_total=raw["n_total"],
            n_shots=n_shots,
            subjects=raw.get("subjects", subjects or []),
            per_subject=raw.get("per_subject", {}),
            latency_ms=elapsed,
            details=raw.get("details", []) if self.record_details else [],
            metadata={
                "agent_name": self.agent_name,
                "benchmark_name": meta.get("name"),
                "category": meta.get("category"),
                **raw.get("metadata", {}),
            },
            owner_agents=meta.get("owner_agents", []),
        )
        logger.info(
            "Eval complete: %s score=%.3f (%d/%d) latency=%.0fms agent=%s",
            benchmark_key,
            result.overall_score,
            result.n_correct,
            result.n_total,
            result.latency_ms,
            self.agent_name,
        )
        return result
