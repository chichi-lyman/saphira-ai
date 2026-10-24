# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Face perception & enrollment endpoints (Aura + NovaAethrea).
# Privacy-first: enrollment requires explicit consent_token.

from __future__ import annotations

import logging
import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.aura import AuraAgent
from agents.novaaethrea import NovaAethreaAgent

logger = logging.getLogger("saphira.api.face")

router = APIRouter(prefix="/face", tags=["face"])

_aura = AuraAgent()
_memory = NovaAethreaAgent()


class FacePerceiveRequest(BaseModel):
    image_b64: str = Field(..., description="Base64-encoded JPEG/PNG")
    return_embeddings: bool = False


class FaceEnrollRequest(BaseModel):
    image_b64: str = Field(..., description="Base64-encoded JPEG/PNG of the face to remember")
    label: str = Field(..., min_length=1, max_length=64)
    consent_token: str = Field(..., min_length=8, description="Token proving explicit user consent")
    metadata: Optional[Dict[str, Any]] = None


class ConsentTokenResponse(BaseModel):
    consent_token: str
    expires_note: str = "Single-use style token for enrollment; generate only after user says yes."


@router.post("/perceive")
async def perceive_face(body: FacePerceiveRequest) -> Dict[str, Any]:
    """
    Run face detection + recognition against currently stored consented faces.
    Does not store anything.
    """
    known = _memory.get_known_faces_for_perception()
    result = _aura.perceive(
        {
            "type": "face",
            "image_b64": body.image_b64,
            "known_faces": known,
            "return_embeddings": body.return_embeddings,
        }
    )
    return result


@router.post("/enroll")
async def enroll_face(body: FaceEnrollRequest) -> Dict[str, Any]:
    """
    Extract embedding via Aura, then persist via NovaAethrea.
    Requires a consent_token obtained after the user explicitly agrees.
    """
    enroll_result = _aura.enroll_face(
        image_payload={"image_b64": body.image_b64},
        label=body.label,
        consent_token=body.consent_token,
    )
    if enroll_result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=enroll_result)

    store_result = _memory.store_face(
        label=body.label,
        embedding=enroll_result["embedding"],
        consent_token=body.consent_token,
        metadata=body.metadata,
    )
    if store_result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=store_result)

    return {
        "status": "ok",
        "label": body.label,
        "message": f"I will remember this face as {body.label}.",
        "embedding_sha256": enroll_result.get("embedding_sha256"),
    }


@router.get("/list")
async def list_faces() -> Dict[str, Any]:
    """List labels of stored faces (no embeddings)."""
    return _memory.list_faces()


@router.delete("/forget/{label}")
async def forget_face(label: str) -> Dict[str, Any]:
    return _memory.forget_face(label)


@router.post("/consent-token", response_model=ConsentTokenResponse)
async def create_consent_token() -> ConsentTokenResponse:
    """
    Generate a short random token the client should request only after
    the user has said yes to remembering a face. The token is not stored
    server-side; it is simply required on the enroll call as proof of intent.
    """
    token = secrets.token_urlsafe(16)
    return ConsentTokenResponse(consent_token=token)
