# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI — Standardized Evaluation Package

"""Standardized academic and coding evaluation benchmarks for Saphira AI.

Primary surfaces:
  - MMLU (Massive Multitask Language Understanding)
  - HumanEval (Python coding, pass@1)
  - MBPP (Mostly Basic Python Problems, pass@1)

Additional benchmarks register via BenchmarkRegistry.
"""

from .registry import BenchmarkRegistry, get_registry
from .runner import EvaluationRunner, EvaluationResult
from .benchmarks.mmlu import MMLUBenchmark, MMLUConfig
from .benchmarks.humaneval import HumanEvalBenchmark, HumanEvalConfig
from .benchmarks.mbpp import MBPPBenchmark, MBPPConfig

__all__ = [
    "BenchmarkRegistry",
    "get_registry",
    "EvaluationRunner",
    "EvaluationResult",
    "MMLUBenchmark",
    "MMLUConfig",
    "HumanEvalBenchmark",
    "HumanEvalConfig",
    "MBPPBenchmark",
    "MBPPConfig",
]
