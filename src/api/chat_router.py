# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Public conversational surface: execution + natural Saphira dialogue + session memory.
# Multimodal: optional image_b64 for face recognition turns.
# Brain: all natural language generation goes through SaphiraBrain (persona-locked).

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core.orchestrator import SaphiraOrchestrator
from src.core.saphira_brain import get_saphira_brain
from src.core.saphira_translator import public_reply
from src.avatar.grok_avatar_service import avatar_service
from src.memory.persistent_store import persistent_memory

router = APIRouter(prefix="/chat", tags=["chat"])
_orchestrator = SaphiraOrchestrator()
_brain = get_saphira_brain()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    confirmed: bool = False
    room: Optional[str] = None
    session_id: Optional[str] = None
    # Multimodal face support
    image_b64: Optional[str] = Field(
        default=None,
        description="Optional base64 JPEG/PNG for face recognition / enrollment",
    )
    consent_token: Optional[str] = Field(
        default=None,
        description="One-time token proving user consented to remember a face",
    )


def _session_history(session_id: Optional[str], limit: int = 12) -> list[dict[str, str]]:
    if not session_id:
        return []
    history = persistent_memory.get_history(limit=60)
    session = [item for item in history if item.get("session_id") == session_id]
    return session[-limit:]


def _conversation_context(
    user_message: str,
    task_result: Dict[str, Any],
    history: list[dict[str, str]],
) -> str:
    safe_message = str(task_result.get("message") or task_result.get("raw_output") or "")
    status = task_result.get("status", "success")

    history_text = "\n".join(
        f"{item.get('role', 'user').upper()}: {item.get('text', '')}" for item in history
    ) or "No earlier messages in this session."

    return f"""[CONVERSATION MODE]
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


@router.post("")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    """Main Saphira conversation endpoint: execute, remember, and respond naturally."""
    context = {
        "confirmed": req.confirmed,
        "room": req.room,
        "session_id": req.session_id,
        "image_b64": req.image_b64,
        "consent_token": req.consent_token,
    }

    result = await _orchestrator.process(req.message, context=context)
    final = result.get("final", {})
    avatar_state = result.get("avatar_state", "talking")

    history = _session_history(req.session_id)
    ctx = _conversation_context(req.message, final, history)

    # Brain path: persona + competitive directive always injected
    natural_message = await _brain.reply(req.message, conversation_context=ctx)
    public_message = natural_message or public_reply(req.message, final) or final.get("message")

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
        "requires_confirmation": final.get("status") in ("needs_confirmation",) or final.get("requires_consent", False),
        "intent": final.get("intent"),
        "session_id": req.session_id,
        "voice_ready": True,
        "matches": final.get("matches"),
        "faces_detected": final.get("faces_detected"),
        "owner": "Chelsea Megan Woods",
        "brain": "SaphiraBrain",
    }
