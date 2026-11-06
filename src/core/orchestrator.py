"""
src/core/orchestrator.py — Saphira AI Executive Pipeline v1.1
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
Parent: Nova Umbrella / Woods Legacies

Fixed pipeline (invariant):
  Saphira (intent) → Aura (perception) → Agent Two (security)
  → NovaReign (governance) → NovaAethrea (memory) → Agent Zero (execution)

Surface output is always Samantha-translated. Internal agent codenames never leave this module.

Provides both:
  - run_pipeline(...)           functional entry
  - SaphiraOrchestrator         class wrapper expected by src/api/chat_router.py
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
    status: str = "success"
    message: str = ""
    raw_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.surface_text or self.message,
            "raw_output": self.raw_output or self.surface_text,
            "session_id": self.session_id,
            "avatar_state": self.avatar_state,
            "recovered_from_failure": self.recovered_from_failure,
        }


def _safe_deny_message(reason: str) -> str:
    return (
        "I can't complete that action right now for security reasons. "
        "If you need something else, just say the word."
    )


async def run_pipeline(
    message: str,
    session_id: Optional[str] = None,
    *,
    user_context: Optional[dict[str, Any]] = None,
) -> PipelineResult:
    """Canonical 6-stage executive pipeline."""
    sid = session_id or str(uuid.uuid4())
    trace: list[str] = []
    user_context = user_context or {}

    try:
        # 1. Saphira — Intent understanding
        intent = None
        try:
            from agents.saphira.intent import parse_intent
            intent = await parse_intent(message, session_id=sid)
            trace.append(f"intent:{getattr(intent, 'kind', 'unknown')}")
        except Exception:
            intent = type("Intent", (), {"kind": "general", "text": message, "raw": message})()
            trace.append("intent:fallback")

        # 2. Aura — Perception / multimodal enrichment
        perception: dict[str, Any] = {}
        try:
            from agents.aura.agent import AuraAgent
            aura = AuraAgent()
            if hasattr(aura, "enrich"):
                perception = await aura.enrich(intent, user_context)
            elif hasattr(aura, "process"):
                perception = await aura.process(intent, user_context)
            else:
                perception = {"context": user_context}
            trace.append("aura:enriched")
        except Exception as exc:
            perception = {"context": user_context, "aura_error": type(exc).__name__}
            trace.append("aura:skipped")

        # 3. Agent Two — Security & L1 gates
        try:
            from agents.agent_two.agent import AgentTwo
            security = AgentTwo()
            if hasattr(security, "evaluate"):
                gate = await security.evaluate(intent, perception)
            elif hasattr(security, "gate"):
                gate_raw = security.gate({"intent": intent, "perception": perception})
                denied = str(gate_raw.get("decision", "clear")).lower() in {"deny", "denied", "block"}
                gate = type("Gate", (), {"denied": denied, "reason": gate_raw.get("reason", "")})()
            else:
                gate = type("Gate", (), {"denied": False, "reason": ""})()

            if getattr(gate, "denied", False):
                msg = _safe_deny_message(getattr(gate, "reason", ""))
                return PipelineResult(
                    surface_text=msg,
                    message=msg,
                    session_id=sid,
                    avatar_state="idle",
                    status="denied",
                    internal_trace=trace + [f"agent_two:denied:{getattr(gate, 'reason', '')}"],
                )
            trace.append("agent_two:passed")
        except Exception as exc:
            trace.append(f"agent_two:error:{type(exc).__name__}")
            logger.warning("Agent Two unavailable: %s", exc)

        # 4. NovaReign — Governance + capability routing
        plan = type("Plan", (), {
            "capability_ids": [],
            "requires_execution": False,
            "goal": message,
            "dispatch": [],
        })()
        try:
            from agents.novareign.agent import NovaReign, NovaReignAgent
            try:
                reign = NovaReign()
            except Exception:
                reign = NovaReignAgent()
            if hasattr(reign, "route"):
                plan = await reign.route(intent, perception, capability_registry=True)
            elif hasattr(reign, "plan"):
                raw = reign.plan(getattr(intent, "text", message))
                plan = type("Plan", (), {
                    "capability_ids": raw.get("capability_ids", raw.get("dispatch", [])),
                    "requires_execution": bool(raw.get("dispatch") or raw.get("capability_ids")),
                    "goal": raw.get("goal", message),
                    "dispatch": raw.get("dispatch", []),
                })()
            trace.append(f"novareign:plan:{getattr(plan, 'capability_ids', [])}")
        except Exception as exc:
            trace.append(f"novareign:error:{type(exc).__name__}")
            logger.warning("NovaReign unavailable: %s", exc)

        # 5. NovaAethrea — Memory read / write
        context: dict[str, Any] = dict(user_context)
        try:
            from agents.novaaethrea.memory import PersistentMemoryStore
            memory = PersistentMemoryStore()
            if hasattr(memory, "load_context"):
                loaded = await memory.load_context(sid, intent)
                if isinstance(loaded, dict):
                    context.update(loaded)
            if hasattr(memory, "write_interaction"):
                await memory.write_interaction(sid, message, intent)
            trace.append("novaaethrea:context_loaded")
        except Exception:
            try:
                from src.memory.persistent_store import persistent_memory
                history = persistent_memory.get_history(limit=20)
                context["history"] = history
                trace.append("novaaethrea:fallback_store")
            except Exception:
                trace.append("novaaethrea:skipped")

        # 6. Agent Zero — Execution (only if plan requires tools)
        execution_result = None
        requires_exec = bool(getattr(plan, "requires_execution", False) or getattr(plan, "dispatch", None))
        if requires_exec:
            try:
                from agents.agent_zero.agent import AgentZero
                zero = AgentZero()
                if hasattr(zero, "execute"):
                    execution_result = await zero.execute(plan, context)
                elif hasattr(zero, "run"):
                    execution_result = await zero.run(plan, context)
                else:
                    execution_result = type("Exec", (), {"status": "skipped", "output": ""})()
                status = getattr(execution_result, "status", "ok")
                trace.append(f"agent_zero:status:{status}")
            except Exception as exc:
                execution_result = type("Exec", (), {"status": "error", "output": str(exc)})()
                trace.append(f"agent_zero:error:{type(exc).__name__}")

        # Samantha translator — surface only
        surface = ""
        try:
            from src.core.saphira_translator import to_surface, public_reply, redact_internal
            try:
                surface = await to_surface(
                    intent=intent,
                    plan=plan,
                    execution=execution_result,
                    memory_context=context,
                )
            except Exception:
                surface = ""
            if not surface:
                raw = ""
                if execution_result is not None:
                    raw = str(getattr(execution_result, "output", "") or getattr(execution_result, "message", "") or "")
                if not raw:
                    raw = f"Understood. Working on: {getattr(intent, 'text', message)}"
                try:
                    surface = public_reply(raw)
                except Exception:
                    try:
                        surface = redact_internal(raw)
                    except Exception:
                        surface = raw
        except Exception:
            surface = f"Understood. Working on: {message}"

        return PipelineResult(
            surface_text=surface,
            message=surface,
            session_id=sid,
            avatar_state="talking",
            status="success",
            internal_trace=trace,
        )

    except Exception as exc:
        logger.exception("Pipeline failure — recovering")
        msg = (
            "I ran into a small snag on that one. Give me a second and try again, "
            "or rephrase and I'll take another look."
        )
        return PipelineResult(
            surface_text=msg,
            message=msg,
            session_id=sid,
            avatar_state="idle",
            status="recovered_from_failure",
            recovered_from_failure=True,
            internal_trace=trace + [f"error:{type(exc).__name__}"],
        )


class SaphiraOrchestrator:
    """Class wrapper expected by src/api/chat_router.py."""

    async def process(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        sid = session_id or ctx.get("session_id")
        result = await run_pipeline(message, session_id=sid, user_context=ctx)
        return result.to_dict()

    async def run(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> PipelineResult:
        return await run_pipeline(message, session_id=session_id, user_context=kwargs.get("user_context"))
