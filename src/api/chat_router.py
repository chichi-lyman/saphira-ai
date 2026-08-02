# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Public chat surface: orchestrator + Samantha translator + avatar state.

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core.orchestrator import SaphiraOrchestrator
from src.core.saphira_translator import SaphiraTranslator
from src.avatar.grok_avatar_service import avatar_service

router = APIRouter(prefix="/chat", tags=["chat"])
_orchestrator = SaphiraOrchestrator()
_translator = SaphiraTranslator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    confirmed: bool = False
    room: Optional[str] = None
    session_id: Optional[str] = None


@router.post("")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    """
    Main public interaction endpoint.
    Returns warm persona text + avatar_state for Flutter holographic UI.
    """
    context = {
        "confirmed": req.confirmed,
        "room": req.room,
        "session_id": req.session_id,
    }
    result = await _orchestrator.process(req.message, context=context)
    final = result.get("final", {})
    avatar_state = result.get("avatar_state", "talking")

    # Warm public-facing line (never expose agent names)
    try:
        public_message = _translator.to_public(final)
    except Exception:
        public_message = final.get("message") or "I heard you — working on it."

    # Optional: refresh avatar still for this state (stub-safe without API key)
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
        "owner": "Chelsea Megan Woods",
    }
