# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
FastAPI routes for Saphira public avatar generation & state control.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.avatar.grok_avatar_service import avatar_service, AvatarState

router = APIRouter(prefix="/avatar", tags=["avatar"])


class FrameRequest(BaseModel):
    state: str = Field("idle", description="idle | welcome | talking | thinking | listening | glow | confirm")
    extra_action: str = ""
    reference_url: Optional[str] = None
    aspect_ratio: str = "9:16"


class ClipRequest(BaseModel):
    state: str = Field("talking")
    extra_action: str = ""
    reference_url: Optional[str] = None
    duration_sec: int = Field(4, ge=2, le=10)


class ReferenceRequest(BaseModel):
    url: str = Field(..., description="Public HTTPS URL of master Chelsea reference image")


@router.get("/status")
async def avatar_status():
    return avatar_service.status()


@router.post("/frame")
async def generate_frame(req: FrameRequest):
    if req.state not in {s.value for s in AvatarState}:
        raise HTTPException(status_code=400, detail=f"Unknown state: {req.state}")
    return avatar_service.generate_frame(
        state=req.state,
        extra_action=req.extra_action,
        reference_url=req.reference_url,
        aspect_ratio=req.aspect_ratio,
    )


@router.post("/clip")
async def generate_clip(req: ClipRequest):
    if req.state not in {s.value for s in AvatarState}:
        raise HTTPException(status_code=400, detail=f"Unknown state: {req.state}")
    return avatar_service.generate_clip(
        state=req.state,
        extra_action=req.extra_action,
        reference_url=req.reference_url,
        duration_sec=req.duration_sec,
    )


@router.post("/reference")
async def set_reference(req: ReferenceRequest):
    return avatar_service.set_reference(req.url)


@router.get("/states")
async def list_states():
    from src.avatar.grok_avatar_service import STATE_PROMPTS

    return {"states": STATE_PROMPTS, "owner": "Chelsea Megan Woods"}
