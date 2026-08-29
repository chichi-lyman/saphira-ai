# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Twilio Voice HTTP surface: outbound call API, TwiML endpoints, status webhooks.

Outbound placement always requires confirmed=True so the executive runtime /
CommercialAuthorityPolicy can gate side effects. TwiML endpoints are public
to Twilio's infrastructure; they only return static or prompt-driven XML.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Form, HTTPException, Query, Response
from pydantic import BaseModel, Field

from src.connectors.twilio_connector import TwilioConnector, twilio_connector_from_env

logger = logging.getLogger("SaphiraTwilioVoice")

router = APIRouter(prefix="/twilio/voice", tags=["twilio-voice"])


class OutboundCallRequest(BaseModel):
    to: str = Field(..., min_length=3, max_length=32, description="E.164 destination")
    say_text: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Spoken message when twiml_url is not provided",
    )
    twiml_url: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="Absolute URL that returns TwiML for the call",
    )
    voice: str = Field(default="alice", max_length=32)
    language: str = Field(default="en-US", max_length=16)
    timeout_seconds: int = Field(default=30, ge=5, le=600)
    confirmed: bool = Field(
        default=False,
        description="Must be true after policy approval to place the call",
    )


class HangupRequest(BaseModel):
    call_sid: str = Field(..., min_length=10, max_length=64)
    confirmed: bool = False


def _connector() -> TwilioConnector:
    return twilio_connector_from_env()


@router.get("/status")
async def voice_status() -> Dict[str, Any]:
    health = _connector().health()
    return {
        "provider": "twilio",
        "component": "voice",
        **health,
    }


@router.post("/call")
async def place_outbound_call(body: OutboundCallRequest) -> Dict[str, Any]:
    """Place an outbound Twilio call. Requires confirmed=True."""
    if not body.confirmed:
        raise HTTPException(
            status_code=403,
            detail="Outbound voice calls require confirmed=True after policy approval",
        )
    if not body.say_text and not body.twiml_url:
        raise HTTPException(
            status_code=400,
            detail="Provide say_text or twiml_url",
        )

    result = _connector().start_voice_call(
        body.to,
        twiml_url=body.twiml_url,
        say_text=body.say_text,
        voice=body.voice,
        language=body.language,
        timeout_seconds=body.timeout_seconds,
        approved=True,
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=502, detail=result.get("message", "Twilio error"))
    if result.get("status") == "denied":
        raise HTTPException(status_code=403, detail=result.get("message"))
    return result


@router.get("/calls/{call_sid}")
async def get_call_status(call_sid: str) -> Dict[str, Any]:
    result = _connector().get_call(call_sid)
    if result.get("status") == "error":
        code = 404 if result.get("http_status") == 404 else 502
        raise HTTPException(status_code=code, detail=result.get("message", "Twilio error"))
    return result


@router.post("/hangup")
async def hangup_call(body: HangupRequest) -> Dict[str, Any]:
    if not body.confirmed:
        raise HTTPException(
            status_code=403,
            detail="Hangup requires confirmed=True after policy approval",
        )
    result = _connector().hangup_call(body.call_sid, approved=True)
    if result.get("status") == "error":
        raise HTTPException(status_code=502, detail=result.get("message", "Twilio error"))
    return result


@router.get("/twiml/say")
@router.post("/twiml/say")
async def twiml_say(
    text: str = Query(default="Hello from Saphira AI.", max_length=4000),
    voice: str = Query(default="alice", max_length=32),
    language: str = Query(default="en-US", max_length=16),
) -> Response:
    """Return TwiML that speaks ``text``. Used as Call Url target."""
    xml = TwilioConnector.build_say_twiml(text, voice=voice, language=language)
    return Response(content=xml, media_type="application/xml")


@router.get("/twiml/gather")
@router.post("/twiml/gather")
async def twiml_gather(
    prompt: str = Query(default="Please press 1 to confirm.", max_length=2000),
    action_url: str = Query(..., max_length=2048),
    num_digits: int = Query(default=1, ge=1, le=32),
    timeout: int = Query(default=5, ge=1, le=30),
    voice: str = Query(default="alice", max_length=32),
    language: str = Query(default="en-US", max_length=16),
) -> Response:
    xml = TwilioConnector.build_gather_twiml(
        prompt,
        action_url=action_url,
        num_digits=num_digits,
        timeout=timeout,
        voice=voice,
        language=language,
    )
    return Response(content=xml, media_type="application/xml")


@router.post("/webhook/status")
async def voice_status_webhook(
    CallSid: Optional[str] = Form(default=None),
    CallStatus: Optional[str] = Form(default=None),
    To: Optional[str] = Form(default=None),
    From: Optional[str] = Form(default=None),
    CallDuration: Optional[str] = Form(default=None),
) -> Dict[str, Any]:
    """Twilio status callback receiver. Logs lifecycle events; no secrets returned."""
    logger.info(
        "Twilio voice status CallSid=%s status=%s to=%s from=%s duration=%s",
        CallSid,
        CallStatus,
        To,
        From,
        CallDuration,
    )
    return {
        "status": "ok",
        "call_sid": CallSid,
        "call_status": CallStatus,
    }
