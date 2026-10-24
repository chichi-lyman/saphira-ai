"""Autonomous self-repair fabric for Nova Umbrella / Saphira Tier S.

Decomposes every competitive score into atomic primitives that can detect
failure, repair, and re-verify without human intervention.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from .atomic_scores import ATOMIC_PRIMITIVES, AtomicPrimitive, decompose_score
from .loop_guard import LoopGuard, LoopVerdict
from .self_repair import SelfRepairEngine, RepairReport
from .scoreboard import TierSScoreboard, scoreboard

__all__ = [
    "ATOMIC_PRIMITIVES",
    "AtomicPrimitive",
    "decompose_score",
    "LoopGuard",
    "LoopVerdict",
    "SelfRepairEngine",
    "RepairReport",
    "TierSScoreboard",
    "scoreboard",
]
