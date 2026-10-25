# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI — Standardized Evaluation Package

"""Standardized academic, coding, and graduate science evaluation benchmarks.

Surfaces:
  - MMLU (Massive Multitask Language Understanding)
  - HumanEval / MBPP (Python coding, pass@1)
  - GPQA (Graduate-Level Google-Proof Q&A)

Additional benchmarks register via BenchmarkRegistry.
"""

from .registry import BenchmarkRegistry, get_registry
from .runner import EvaluationRunner, EvaluationResult
from .benchmarks.mmlu import MMLUBenchmark, MMLUConfig
from .benchmarks.humaneval import HumanEvalBenchmark, HumanEvalConfig
from .benchmarks.mbpp import MBPPBenchmark, MBPPConfig
from .benchmarks.gpqa import GPQABenchmark, GPQAConfig

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
    "GPQABenchmark",
    "GPQAConfig",
]
