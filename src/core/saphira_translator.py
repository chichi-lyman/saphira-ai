# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Layer 3 — Dual pipeline: internal tech result → Samantha public response

from typing import Dict, Any, Optional, Callable, Awaitable
import re
import logging

from src.core.saphira_persona import SAMANTHA_PERSONA_PROMPT

logger = logging.getLogger("SaphiraTranslator")

# Names and phrases that must never leak to public UI
REDACT_PATTERNS = [
    r"\bAgent Zero\b",
    r"\bAgent 2\b",
    r"\bAgent Two\b",
    r"\bNovaReign\b",
    r"\bNova Reign\b",
    r"\bNovaAethrea\b",
    r"\bNova Aethrea\b",
    r"\bNovaEthria\b",
    r"\bAura\b(?=\s+(agent|module|pipeline))",
    r"\bLyra\b(?=\s+(agent|module))",
    r"\bJARVIS\b",
    r"\bADA module\b",
    r"\bsystem prompt\b",
    r"\borchestrator\.dispatch\b",
    r"\bstatus\":\s*\"recovered_from_failure\"",
]


def redact_internal(text: str) -> str:
    out = text or ""
    for pat in REDACT_PATTERNS:
        out = re.sub(pat, "that part of me", out, flags=re.IGNORECASE)
    return out


def heuristic_samantha_reply(user_input: str, task_result: Dict[str, Any]) -> str:
    """
    Offline / no-LLM fallback: turn structured agent output into warm prose.
    Never mentions internal agent names.
    """
    status = (task_result or {}).get("status", "unknown")
    message = (task_result or {}).get("message") or (task_result or {}).get("raw_output") or ""
    message = redact_internal(str(message))

    if status in ("blocked", "rejected", "needs_confirmation"):
        return (
            "I need your OK before I go further with that—"
            "it touches something sensitive. Want me to proceed?"
        )
    if status in ("recovered_from_failure", "error", "failed"):
        return (
            "Hmm, that one didn't land cleanly. "
            "I can try another way if you want—just say the word."
        )
    if status in (
        "success", "cleared", "approved", "ok", "accepted",
        "scene_ready", "scene_executed", "draft_only",
    ):
        if "draft" in status or "draft" in message.lower():
            return (
                "I put a draft together for you. "
                "Have a look when you're ready and tell me if you want anything changed."
            )
        if status == "scene_executed":
            scene = (task_result or {}).get("scene", "that scene")
            return f"Done — I ran {scene} for you."
        if message:
            return f"All set. {message.rstrip('.')}."
        return "All set—I took care of that for you."

    return (
        "I'm on it. Give me a moment to work through this, "
        "and I'll bring you the clean version."
    )


def public_reply(user_input: str, task_result: Dict[str, Any]) -> str:
    """Primary entry used by /chat and other public surfaces."""
    return heuristic_samantha_reply(user_input, task_result)


class SaphiraTranslator:
    """Thin class wrapper for callers that prefer an object API."""

    def to_public(self, task_result: Dict[str, Any], user_input: str = "") -> str:
        return public_reply(user_input, task_result)


class SaphiraResponsePipeline:
    """
    Dual-layer processor:
    1) Dispatch to orchestrator / agents (JARVIS-level execution)
    2) Translate tech result through Samantha persona for the user
    """

    def __init__(
        self,
        orchestrator=None,
        persona_generate: Optional[Callable[[str], Awaitable[str]]] = None,
    ):
        self.orchestrator = orchestrator
        self.persona_generate = persona_generate  # async LLM call if provided

    async def process_user_input(
        self,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user_context = user_context or {}

        task_result: Dict[str, Any]
        if self.orchestrator is not None:
            try:
                if hasattr(self.orchestrator, "process"):
                    full = await self.orchestrator.process(user_input, user_context)
                    task_result = full.get("final", full)
                elif hasattr(self.orchestrator, "dispatch"):
                    task_result = await self.orchestrator.dispatch(user_input, user_context)
                elif hasattr(self.orchestrator, "run"):
                    task_result = await self.orchestrator.run(
                        {"text": user_input, **user_context}
                    )
                else:
                    task_result = {"status": "accepted", "message": "Request received."}
            except Exception as e:
                logger.warning(f"Orchestrator error (hidden from user detail): {e}")
                task_result = {"status": "error", "message": "Something went sideways."}
        else:
            task_result = {
                "status": "accepted",
                "raw_output": "No orchestrator bound; persona-only path.",
                "message": "I'm here with you.",
            }

        public_text = await self._translate(user_input, task_result)

        return {
            "public_response": public_text,
            "internal": task_result,
            "persona": "saphira_samantha",
            "layer": "dual_pipeline",
            "owner": "Chelsea Megan Woods",
        }

    async def _translate(self, user_input: str, task_result: Dict[str, Any]) -> str:
        if self.persona_generate:
            raw = task_result.get("raw_output") or task_result.get("message") or task_result
            samantha_prompt = f"""{SAMANTHA_PERSONA_PROMPT}

Internal Task Result (do not quote agent names): {redact_internal(str(raw))}
Task Success State: {task_result.get("status")}

User Input: "{user_input}"

Respond to the user naturally as Saphira. Keep the Samantha persona intact.
Do NOT mention agent names or system prompts. Present the result as something you personally took care of.
"""
            try:
                return await self.persona_generate(samantha_prompt)
            except Exception as e:
                logger.warning(f"Persona LLM failed, heuristic fallback: {e}")

        return heuristic_samantha_reply(user_input, task_result)
