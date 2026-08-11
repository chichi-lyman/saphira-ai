"""Saphira TikTok OAuth + Content Posting API routes."""

from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, Field, HttpUrl

from src.integrations.tiktok_content_posting import (
    TikTokAPIError,
    TikTokConfigError,
    TikTokContentPostingService,
)

router = APIRouter(prefix="/tiktok", tags=["TikTok"])


def service() -> TikTokContentPostingService:
    try:
        return TikTokContentPostingService()
    except TikTokConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def require_automation_key(x_saphira_automation_key: str | None) -> None:
    expected = os.getenv("SAPHIRA_TIKTOK_AUTOMATION_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="SAPHIRA_TIKTOK_AUTOMATION_KEY is not configured.")
    if not x_saphira_automation_key or not secrets.compare_digest(x_saphira_automation_key, expected):
        raise HTTPException(status_code=401, detail="Unauthorized TikTok automation request.")


class PublishVideoRequest(BaseModel):
    video_url: HttpUrl
    title: str = Field(min_length=1, max_length=2200)
    privacy_level: str = "PUBLIC_TO_EVERYONE"
    disable_comment: bool = False
    disable_duet: bool = False
    disable_stitch: bool = False
    video_cover_timestamp_ms: int = Field(default=0, ge=0)


@router.get("/oauth/start")
async def oauth_start():
    svc = service()
    state = await svc.create_oauth_state()
    return {"authorization_url": svc.authorization_url(state)}


@router.get("/oauth/callback")
async def oauth_callback(code: str | None = None, state: str | None = None, error: str | None = None):
    svc = service()
    if error:
        raise HTTPException(status_code=400, detail=f"TikTok authorization failed: {error}")
    if not code or not state or not await svc.consume_oauth_state(state):
        raise HTTPException(status_code=400, detail="Invalid or expired TikTok OAuth callback.")
    try:
        token = await svc.exchange_code(code)
    except TikTokAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    frontend = os.getenv("SAPHIRA_WEB_ORIGIN", "")
    if frontend:
        return Response(
            status_code=302,
            headers={"Location": f"{frontend.rstrip('/')}/settings/tiktok?connected=1&open_id={token.open_id}"},
            media_type="text/plain",
        )
    return {"connected": True, "open_id": token.open_id, "scope": token.scope}


@router.post("/connect/code")
async def connect_code(code: str):
    """Exchange a short-lived authorization code over HTTPS; never expose client_secret."""
    svc = service()
    try:
        token = await svc.exchange_code(code)
    except TikTokAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"connected": True, "open_id": token.open_id, "scope": token.scope}


@router.get("/creator-info/{open_id}")
async def creator_info(open_id: str, x_saphira_automation_key: str | None = Header(default=None)):
    require_automation_key(x_saphira_automation_key)
    svc = service()
    try:
        return await svc.creator_info(open_id)
    except TikTokAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.post("/publish/{open_id}")
async def publish(
    open_id: str,
    payload: PublishVideoRequest,
    x_saphira_automation_key: str | None = Header(default=None),
):
    require_automation_key(x_saphira_automation_key)
    svc = service()
    try:
        result = await svc.direct_post_video(
            open_id,
            video_url=str(payload.video_url),
            title=payload.title,
            privacy_level=payload.privacy_level,
            disable_comment=payload.disable_comment,
            disable_duet=payload.disable_duet,
            disable_stitch=payload.disable_stitch,
            video_cover_timestamp_ms=payload.video_cover_timestamp_ms,
        )
    except TikTokAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc
    return {"submitted": True, **result}


@router.post("/status/{open_id}/{publish_id:path}")
async def status(
    open_id: str,
    publish_id: str,
    x_saphira_automation_key: str | None = Header(default=None),
):
    require_automation_key(x_saphira_automation_key)
    svc = service()
    try:
        return await svc.publish_status(open_id, publish_id)
    except TikTokAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.delete("/disconnect/{open_id}")
async def disconnect(open_id: str, x_saphira_automation_key: str | None = Header(default=None)):
    require_automation_key(x_saphira_automation_key)
    svc = service()
    await svc.disconnect(open_id)
    return {"connected": False}
