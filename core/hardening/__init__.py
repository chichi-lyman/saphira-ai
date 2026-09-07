"""Saphira runtime hardening primitives.

These primitives are intentionally dependency-light and deterministic. They sit
between planning and execution so that model output can never be treated as
authority by itself.
"""

from .kernel import (
    Action,
    ActionClass,
    Decision,
    ExecutionEnvelope,
    HardeningKernel,
)

__all__ = [
    "Action",
    "ActionClass",
    "Decision",
    "ExecutionEnvelope",
    "HardeningKernel",
]
