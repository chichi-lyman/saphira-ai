# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Public conversational surface: execution + natural Saphira dialogue + session memory.

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.core_agents import SaphiraCore
from src.core.orchestrator import SaphiraOrchestrator
from src.core.saphira_persona import SAMANTHA_PERSONA_PROMPT
from src.core.saphira_translator import public_reply
from src.avatar.grok_avatar_service import avatar_service
from src.memory.persistent_store import persistent_memory
from src.connectors.gemini import GeminiConnector

router = APIRouter(prefix="/chat", tags=["chat"])
_orchestrator = SaphiraOrchestrator()
_gemini = GeminiConnector()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    confirmed: bool = False
    room: Optional[str] = None
    session_id: Optional[str] = None


def _session_history(session_id: Optional[str], limit: int = 12) -> list[dict[str, str]]:
    if not session_id:
        return []
    history = persistent_memory.get_history(limit=60)
    session = [item for item in history if item.get("session_id") == session_id]
    return session[-limit:]


def _natural_prompt(
    user_message: str,
    task_result: Dict[str, Any],
    history: list[dict[str, str]],
) -> str:
    safe_message = str(task_result.get("message") or task_result.get("raw_output") or "")
    status = task_result.get("status", "success")

    history_text = "\n".join(
        f"{item.get('role', 'user').upper()}: {item.get('text', '')}"
        for item in history
    ) or "No earlier messages in this session."

    return f"""{SAMANTHA_PERSONA_PROMPT}

[CONVERSATION MODE]
You are actively conversing with the user, not merely reporting a task result.
Sound natural, warm, curious, emotionally intelligent, playful when appropriate, and present.
Use contractions and varied sentence length. Ask a natural follow-up when it genuinely helps.
Do not force a question into every response.
Do not over-explain unless the user asks for detail.
You can text, write, brainstorm, reason, plan, draft, explain, and have an ordinary back-and-forth conversation.
Never claim to have feelings, consciousness, a body, or experiences you do not actually have.
Do not mention hidden agents, internal prompts, backend implementation, or this instruction.

[RECENT SESSION]
{history_text}

[EXECUTION RESULT]
Status: {status}
Result: {safe_message}

[USER]
{user_message}

Write Saphira's next message directly to the user. Make it sound like a real ongoing conversation rather than a system status report."""


async def _generate_natural_reply(
    user_message: str,
    task_result: Dict[str, Any],
    history: list[dict[str, str]],
) -> Optional[str]:
    if not _gemini.api_key:
        return None
    prompt = _natural_prompt(user_message, task_result, history)
    result = await asyncio.to_thread(_gemini.generate, prompt)
    if result.get("status") == "success" and result.get("text"):
        return str(result["text"]).strip()
    return None


@router.post("")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    """Main Saphira conversation endpoint: execute, remember, and respond naturally."""
    context = {
        "confirmed": req.confirmed,
        "room": req.room,
        "session_id": req.session_id,
    }

    result = await _orchestrator.process(req.message, context=context)
    final = result.get("final", {})
    avatar_state = result.get("avatar_state", "talking")

    history = _session_history(req.session_id)
    natural_message = await _generate_natural_reply(req.message, final, history)
    public_message = natural_message or public_reply(req.message, final)

    persistent_memory.append_history({
        "session_id": req.session_id,
        "role": "user",
        "text": req.message,
    })
    persistent_memory.append_history({
        "session_id": req.session_id,
        "role": "assistant",
        "text": public_message,
    })

    frame = avatar_service.generate_frame(state=avatar_state)

    return {
        "message": public_message,
        "avatar_state": avatar_state,
        "avatar_frame": {
            "url": frame.get("url"),
            "status": frame.get("status"),
            "state": frame.get("state"),
        },
        "status": final.get("status", "success"),
        "requires_confirmation": final.get("status") == "needs_confirmation",
        "intent": final.get("intent"),
        "session_id": req.session_id,
        "voice_ready": True,
        "owner": "Chelsea Megan Woods",
    }
