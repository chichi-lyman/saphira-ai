"""Autonomy API — self-repair and Tier S scoreboard.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.autonomy.self_repair import SelfRepairEngine
from src.autonomy.scoreboard import scoreboard
from src.autonomy.atomic_scores import decompose_score, primitives_for_agent, ATOMIC_PRIMITIVES

router = APIRouter(prefix="/v1/autonomy", tags=["autonomy-self-repair"])
_engine = SelfRepairEngine()


class RepairRequest(BaseModel):
    agent: Optional[str] = Field(
        default=None,
        description="Agent key to repair, or omit for full ecosystem",
    )
    task: str = "autonomous repair probe"
    prefer_gpu: bool = True
    force_offline: bool = False
    session_id: str = "repair"


@router.post("/repair")
async def run_repair(body: RepairRequest) -> dict[str, Any]:
    ctx = {
        "task": body.task,
        "prefer_gpu": body.prefer_gpu,
        "force_offline": body.force_offline,
        "session_id": body.session_id,
    }
    if body.agent:
        report = _engine.repair_agent(body.agent, **ctx)
        # light scoreboard touch
        eco = {
            "status": "ok" if report.healthy else "degraded",
            "agents": {
                body.agent.lower(): {
                    "healthy": report.healthy,
                    "repaired": report.repaired,
                    "failed": report.failed,
                    "checks": [
                        {
                            "id": s.primitive_id,
                            "ok": s.ok,
                            "observed": s.observed,
                            "msg": s.message,
                        }
                        for s in report.checked
                    ],
                }
            },
        }
        scoreboard.apply_repair_result(eco)
        return {
            "status": "ok" if report.healthy else "degraded",
            "agent": body.agent,
            "repaired": report.repaired,
            "failed": report.failed,
            "elapsed_ms": report.elapsed_ms,
            "checks": eco["agents"][body.agent.lower()]["checks"],
            "scoreboard": scoreboard.snapshot(),
        }

    eco = _engine.repair_ecosystem(**ctx)
    scoreboard.apply_repair_result(eco)
    return {**eco, "scoreboard": scoreboard.snapshot()}


@router.get("/scoreboard")
async def get_scoreboard() -> dict[str, Any]:
    return scoreboard.snapshot()


@router.get("/primitives")
async def list_primitives(agent: Optional[str] = None, score: Optional[str] = None) -> dict[str, Any]:
    if agent:
        items = primitives_for_agent(agent)
    elif score:
        items = decompose_score(score)
    else:
        items = list(ATOMIC_PRIMITIVES)
    return {
        "count": len(items),
        "primitives": [
            {
                "id": p.id,
                "parent_score": p.parent_score,
                "owners": list(p.agent_owners),
                "target": p.target,
                "unit": p.unit,
                "check": p.check,
                "repair_hint": p.repair_hint,
                "severity": p.severity,
            }
            for p in items
        ],
    }
