# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Presence / wake / widget surface for OpenWakeWord + conversational UI.

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.wake_session import wake_sessions, PresenceState
from src.core.background_worker import background_worker
from src.core.orchestrator import SaphiraOrchestrator
from src.core.saphira_translator import public_reply
from src.core.saphira_voice import tts_config
from src.avatar.grok_avatar_service import avatar_service

router = APIRouter(prefix="/presence", tags=["presence", "wake", "widget"])
_orchestrator = SaphiraOrchestrator()


class WakeStartRequest(BaseModel):
    source: str = Field(default="openwakeword", description="openwakeword | widget | node")
    node_id: Optional[str] = None
    custom_greeting: Optional[str] = None


class WakeUtterRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    confirmed: bool = False
    # When true, prefer enqueueing physical/research work as background jobs
    prefer_background: bool = True


class BackgroundEnqueueRequest(BaseModel):
    kind: str = Field(..., description="e.g. iot.lights, iot.vacuum, research")
    payload: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    notify_user: bool = False
    autonomy: str = "L3_autonomous"


@router.post("/wake")
async def wake_start(req: WakeStartRequest) -> Dict[str, Any]:
    """
    Called when OpenWakeWord (or the widget mic button) fires.
    Opens a conversational session and returns a short spoken greeting + widget flags.
    """
    result = wake_sessions.start(
        source=req.source,
        node_id=req.node_id,
        custom_greeting=req.custom_greeting,
    )
    frame = avatar_service.generate_frame(state="talking")
    result["avatar_frame"] = {
        "url": frame.get("url"),
        "status": frame.get("status"),
        "state": frame.get("state"),
    }
    result["tts"] = tts_config("assist")
    return result


@router.post("/utter")
async def wake_utter(req: WakeUtterRequest) -> Dict[str, Any]:
    """
    User spoke after wake. Saphira replies conversationally; heavy work can go background.
    """
    session = wake_sessions.record_user(req.session_id, req.message)
    if not session:
        raise HTTPException(status_code=404, detail="Wake session not found or expired")

    context = {
        "confirmed": req.confirmed,
        "session_id": req.session_id,
        "wake": True,
        "source": session.source,
    }
    result = await _orchestrator.process(req.message, context=context)
    final = result.get("final", {})
    avatar_state = result.get("avatar_state", "talking")

    public_message = public_reply(req.message, final)
    wake_sessions.record_saphira(req.session_id, public_message, talking=True)

    # Soft-signal background work for non-blocking intents
    bg_job_id = None
    intent = final.get("intent") or "general"
    if req.prefer_background and intent not in ("general",) and final.get("status") not in (
        "needs_confirmation",
        "blocked",
        "rejected",
    ):
        # Example: mark that physical follow-through continues quietly
        job = background_worker.enqueue(
            kind="generic",
            payload={
                "summary": f"Following through on {intent}",
                "intent": intent,
                "from_message": req.message[:200],
            },
            notify_user=False,
            session_id=req.session_id,
        )
        bg_job_id = job.id
        wake_sessions.attach_job(req.session_id, job.id)

    frame = avatar_service.generate_frame(state=avatar_state)
    snapshot = wake_sessions.widget_snapshot(req.session_id)

    return {
        "message": public_message,
        "session_id": req.session_id,
        "avatar_state": avatar_state,
        "avatar_frame": {
            "url": frame.get("url"),
            "status": frame.get("status"),
            "state": frame.get("state"),
        },
        "status": final.get("status", "success"),
        "requires_confirmation": final.get("status") == "needs_confirmation",
        "intent": intent,
        "background_job_id": bg_job_id,
        "widget": snapshot.get("widget"),
        "tts": tts_config("confirm_l1" if final.get("status") == "needs_confirmation" else "assist"),
        "owner": "Chelsea Megan Woods",
    }


@router.post("/end")
async def wake_end(session_id: str) -> Dict[str, Any]:
    return wake_sessions.end(session_id)


@router.get("/widget")
async def widget_state(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Poll/subscribe target for Flutter or web floating widget."""
    return wake_sessions.widget_snapshot(session_id)


@router.post("/background")
async def enqueue_background(req: BackgroundEnqueueRequest) -> Dict[str, Any]:
    job = background_worker.enqueue(
        kind=req.kind,
        payload=req.payload,
        autonomy=req.autonomy,
        notify_user=req.notify_user,
        session_id=req.session_id,
    )
    if req.session_id:
        wake_sessions.attach_job(req.session_id, job.id)
    return {"job": job.public_dict(), "owner": "Chelsea Megan Woods"}


@router.get("/background/{job_id}")
async def background_status(job_id: str) -> Dict[str, Any]:
    job = background_worker.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.public_dict()


@router.get("/background")
async def background_list(session_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    return {
        "jobs": background_worker.list_recent(limit=limit, session_id=session_id),
        "owner": "Chelsea Megan Woods",
    }
