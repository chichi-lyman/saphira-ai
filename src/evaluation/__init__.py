# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI — Standardized Evaluation Package

"""Standardized academic and agent evaluation benchmarks for Saphira AI.

Primary surface: MMLU (Massive Multitask Language Understanding).
Additional benchmarks can be registered via the BenchmarkRegistry.
"""

from .registry import BenchmarkRegistry, get_registry
from .runner import EvaluationRunner, EvaluationResult
from .benchmarks.mmlu import MMLUBenchmark, MMLUConfig

__all__ = [
    "BenchmarkRegistry",
    "get_registry",
    "EvaluationRunner",
    "EvaluationResult",
    "MMLUBenchmark",
    "MMLUConfig",
]
