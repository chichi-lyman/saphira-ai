# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""Benchmark registry — maps capability keys to concrete evaluation harnesses.

Owned by: Agent Scholar (knowledge synthesis) + Evaluator (QA/verification)
Governed by: Nova Reign
Routed through: Capability Registry / NovaReign DAG
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type
import logging

logger = logging.getLogger("Saphira.Evaluation.Registry")


class BenchmarkRegistry:
    """Singleton-style registry of standardized evaluation benchmarks."""

    _instance: Optional["BenchmarkRegistry"] = None

    def __init__(self) -> None:
        self._benchmarks: Dict[str, Type] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def instance(cls) -> "BenchmarkRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_defaults()
        return cls._instance

    def register(
        self,
        key: str,
        benchmark_cls: Type,
        *,
        name: str,
        description: str,
        subjects: int = 0,
        category: str = "knowledge",
        owner_agents: Optional[list[str]] = None,
        capability_keys: Optional[list[str]] = None,
    ) -> None:
        """Register a benchmark class under a stable capability key."""
        self._benchmarks[key] = benchmark_cls
        self._metadata[key] = {
            "name": name,
            "description": description,
            "subjects": subjects,
            "category": category,
            "owner_agents": owner_agents or ["scholar", "evaluator"],
            "capability_keys": capability_keys or [f"eval.{key}"],
        }
        logger.info("Registered benchmark %s (%s)", key, name)

    def get(self, key: str) -> Optional[Type]:
        return self._benchmarks.get(key)

    def metadata(self, key: str) -> Optional[Dict[str, Any]]:
        return self._metadata.get(key)

    def list_keys(self) -> list[str]:
        return sorted(self._benchmarks.keys())

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return {k: dict(v) for k, v in self._metadata.items()}

    def _register_defaults(self) -> None:
        # Late import to avoid circular deps
        from .benchmarks.mmlu import MMLUBenchmark

        self.register(
            "mmlu",
            MMLUBenchmark,
            name="MMLU (Massive Multitask Language Understanding)",
            description=(
                "Tests broad academic, factual, and cross-domain reasoning "
                "across 57 subjects spanning humanities, social sciences, STEM, "
                "and professional domains (elementary to professional level)."
            ),
            subjects=57,
            category="knowledge",
            owner_agents=["scholar", "evaluator", "nova_aethrea"],
            capability_keys=[
                "eval.mmlu",
                "eval.mmlu.0shot",
                "eval.mmlu.5shot",
                "knowledge.academic",
                "reasoning.multitask",
            ],
        )


def get_registry() -> BenchmarkRegistry:
    return BenchmarkRegistry.instance()
