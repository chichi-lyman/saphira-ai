"""
src/api/pipeline_chat_router.py — Thin FastAPI surface over the 6-stage orchestrator
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

This router is intentionally small. It only:
  1. Accepts a chat message (+ optional session_id / context)
  2. Calls run_pipeline / SaphiraOrchestrator
  3. Returns surface text + avatar_state + session_id

Existing src/api/chat_router.py remains the richer multimodal path.
This module is the clean end-to-end wiring for the fixed pipeline.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from src.core.orchestrator import SaphiraOrchestrator, run_pipeline

router = APIRouter(prefix="/api/v1", tags=["pipeline-chat"])
_orchestrator = SaphiraOrchestrator()


class PipelineChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User utterance")
    session_id: Optional[str] = None
    room: Optional[str] = None
    auth_token: Optional[str] = Field(
        default=None,
        description="Short-lived PIN / token for high-risk actions (locks, payments)",
    )
    amount: Optional[float] = None
    entity_id: Optional[str] = None


class PipelineChatResponse(BaseModel):
    response: str
    session_id: str
    avatar_state: str = "idle"
    status: str = "success"
    recovered_from_failure: bool = False


def _build_context(req: PipelineChatRequest) -> dict[str, Any]:
    ctx: dict[str, Any] = {}
    if req.room:
        ctx["room"] = req.room
    if req.auth_token:
        ctx["auth_token"] = req.auth_token
        ctx["pin"] = req.auth_token
    if req.amount is not None:
        ctx["amount"] = req.amount
    if req.entity_id:
        ctx["entity_id"] = req.entity_id
    if req.session_id:
        ctx["session_id"] = req.session_id
    return ctx


@router.post("/chat", response_model=PipelineChatResponse)
async def pipeline_chat(req: PipelineChatRequest) -> PipelineChatResponse:
    ctx = _build_context(req)
    result = await run_pipeline(
        req.message,
        session_id=req.session_id,
        user_context=ctx,
    )
    return PipelineChatResponse(
        response=result.surface_text,
        session_id=result.session_id,
        avatar_state=result.avatar_state,
        status=result.status,
        recovered_from_failure=result.recovered_from_failure,
    )


@router.post("/chat/orchestrator", response_model=PipelineChatResponse)
async def pipeline_chat_via_class(req: PipelineChatRequest) -> PipelineChatResponse:
    ctx = _build_context(req)
    data = await _orchestrator.process(req.message, context=ctx, session_id=req.session_id)
    return PipelineChatResponse(
        response=str(data.get("message") or data.get("raw_output") or ""),
        session_id=str(data.get("session_id") or req.session_id or ""),
        avatar_state=str(data.get("avatar_state") or "idle"),
        status=str(data.get("status") or "success"),
        recovered_from_failure=bool(data.get("recovered_from_failure") or False),
    )


@router.websocket("/ws/pipeline")
async def pipeline_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = str(data.get("message") or "").strip()
            if not message:
                await websocket.send_json({"error": "message required"})
                continue
            sid = data.get("session_id")
            ctx = {
                k: data[k]
                for k in ("room", "auth_token", "pin", "amount", "entity_id")
                if k in data and data[k] is not None
            }
            result = await run_pipeline(message, session_id=sid, user_context=ctx)
            await websocket.send_json({
                "response": result.surface_text,
                "session_id": result.session_id,
                "avatar_state": result.avatar_state,
                "status": result.status,
                "recovered_from_failure": result.recovered_from_failure,
            })
    except WebSocketDisconnect:
        return
