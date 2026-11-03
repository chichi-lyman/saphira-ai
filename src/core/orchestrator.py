"""
src/core/orchestrator.py — Saphira AI Executive Pipeline v1.1
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
Parent: Nova Umbrella / Woods Legacies

Fixed pipeline (invariant):
  Saphira (intent) → Aura (perception) → Agent Two (security)
  → NovaReign (governance) → NovaAethrea (memory) → Agent Zero (execution)

Surface output is always Samantha-translated. Internal agent codenames never leave this module.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("saphira.orchestrator")


@dataclass
class PipelineResult:
    surface_text: str
    session_id: str
    avatar_state: str = "idle"
    recovered_from_failure: bool = False
    internal_trace: list[str] = field(default_factory=list)


async def run_pipeline(
    message: str,
    session_id: Optional[str] = None,
    *,
    user_context: Optional[dict[str, Any]] = None,
) -> PipelineResult:
    sid = session_id or str(uuid.uuid4())
    trace: list[str] = []

    try:
        # 1. Saphira — Intent understanding
        from agents.saphira.intent import parse_intent
        intent = await parse_intent(message, session_id=sid)
        trace.append(f"intent:{intent.kind}")

        # 2. Aura — Perception / multimodal enrichment
        from agents.aura.agent import AuraAgent
        aura = AuraAgent()
        perception = await aura.enrich(intent, user_context or {})
        trace.append("aura:enriched")

        # 3. Agent Two — Security & L1 gates
        from agents.agent_two.agent import AgentTwo
        security = AgentTwo()
        gate = await security.evaluate(intent, perception)
        if gate.denied:
            return PipelineResult(
                surface_text=_safe_deny_message(gate.reason),
                session_id=sid,
                avatar_state="idle",
                internal_trace=trace + [f"agent_two:denied:{gate.reason}"],
            )
        trace.append("agent_two:passed")

        # 4. NovaReign — Governance + capability routing
        from agents.novareign.agent import NovaReign
        reign = NovaReign()
        plan = await reign.route(intent, perception, capability_registry=True)
        trace.append(f"novareign:plan:{plan.capability_ids}")

        # 5. NovaAethrea — Memory read / write
        from agents.novaaethrea.memory import PersistentMemoryStore
        memory = PersistentMemoryStore()
        context = await memory.load_context(sid, intent)
        await memory.write_interaction(sid, message, intent)
        trace.append("novaaethrea:context_loaded")

        # 6. Agent Zero — Execution (only if plan requires tools)
        execution_result = None
        if plan.requires_execution:
            from agents.agent_zero.agent import AgentZero
            zero = AgentZero()
            execution_result = await zero.execute(plan, context)
            trace.append(f"agent_zero:status:{execution_result.status}")

        # Samantha translator — surface only
        from src.core.saphira_translator import to_surface
        surface = await to_surface(
            intent=intent,
            plan=plan,
            execution=execution_result,
            memory_context=context,
        )

        return PipelineResult(
            surface_text=surface,
            session_id=sid,
            avatar_state="talking",
            internal_trace=trace,
        )

    except Exception as exc:
        logger.exception("Pipeline failure — recovering")
        return PipelineResult(
            surface_text="I ran into a small snag on that one. Give me a second and try again, or rephrase and I'll take another look.",
            session_id=sid,
            avatar_state="idle",
            recovered_from_failure=True,
            internal_trace=trace + [f"error:{type(exc).__name__}"],
        )


def _safe_deny_message(reason: str) -> str:
    return "I can't complete that action right now for security reasons. If you need something else, just say the word."
