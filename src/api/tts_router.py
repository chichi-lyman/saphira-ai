# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# ElevenLabs TTS endpoint — returns audio bytes or a short-lived proxy URL.
# API key stays server-side. Mobile / web clients never see the secret.

from __future__ import annotations

import os
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from src.core.saphira_voice import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    elevenlabs_payload,
    tts_config,
)

logger = logging.getLogger("SaphiraTTS")

router = APIRouter(prefix="/tts", tags=["tts"])

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2500)
    style: str = Field(default="assist", description="assist | social | confirm_l1")
    product: Optional[str] = "Saphira"


@router.get("/status")
async def tts_status():
    """Health / configuration check (no secrets exposed)."""
    cfg = tts_config()
    return {
        "configured": cfg["configured"],
        "provider": cfg["provider"],
        "voice_set": bool(cfg["voice_id"]),
        "owner": cfg["owner"],
        "product": cfg["product"],
    }


@router.post("")
async def synthesize(req: TTSRequest):
    """
    Generate speech audio via ElevenLabs.
    Returns audio/mpeg bytes directly so the mobile client can play them.
    """
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs not configured. Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID.",
        )

    payload = elevenlabs_payload(req.text, style=req.style)
    if not payload:
        raise HTTPException(status_code=503, detail="Voice ID missing")

    url = f"{ELEVENLABS_BASE}/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("ElevenLabs error %s: %s", resp.status_code, resp.text[:300])
                raise HTTPException(
                    status_code=502,
                    detail=f"ElevenLabs returned {resp.status_code}",
                )
            audio_bytes = resp.content
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ElevenLabs timeout")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("TTS failure")
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=saphira.mp3",
            "Cache-Control": "no-store",
        },
    )
