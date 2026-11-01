# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Inbound webhooks from Zapier / Make / n8n → Saphira

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from src.services.webhook_bridge import get_webhook_bridge

logger = logging.getLogger("Saphira.WebhookRouter")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class InboundEvent(BaseModel):
    type: Optional[str] = None
    event: Optional[str] = None
    action: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "USD"
    source: Optional[str] = None
    row: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class OutboundTrigger(BaseModel):
    target: str = Field(
        ...,
        description="zapier | make | n8n_cross_post | n8n_onboarding | revenue | broadcast",
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    email: Optional[str] = None
    tier: Optional[str] = None


@router.post("/inbound")
async def inbound_webhook(
    request: Request,
    x_saphira_automation_key: Optional[str] = Header(None, alias="X-Saphira-Automation-Key"),
):
    """
    Catch-all inbound endpoint for Zapier, Make, and n8n.

    Configure the automation tool to POST JSON to:
      https://<your-backend>/api/webhooks/inbound
    with header:
      X-Saphira-Automation-Key: <SAPHIRA_AUTOMATION_WEBHOOK_SECRET>
    """
    bridge = get_webhook_bridge()
    if not bridge.verify_inbound(x_saphira_automation_key):
        raise HTTPException(status_code=401, detail="Invalid or missing automation key")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON body required")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    result = bridge.handle_inbound_event(body)
    logger.info("inbound handled: %s", result.get("handled_as"))
    return result


@router.post("/inbound/revenue")
async def inbound_revenue(
    event: InboundEvent,
    x_saphira_automation_key: Optional[str] = Header(None, alias="X-Saphira-Automation-Key"),
):
    """Specialized revenue / tracker sync endpoint."""
    bridge = get_webhook_bridge()
    if not bridge.verify_inbound(x_saphira_automation_key):
        raise HTTPException(status_code=401, detail="Invalid or missing automation key")

    payload = event.dict(exclude_none=True)
    payload.setdefault("type", "revenue_update")
    return bridge.handle_inbound_event(payload)


@router.post("/outbound/trigger")
async def outbound_trigger(
    body: OutboundTrigger,
    x_saphira_automation_key: Optional[str] = Header(None, alias="X-Saphira-Automation-Key"),
):
    """
    Manual / internal trigger of outbound webhooks (secured).
    Useful for testing and for Saphira agents that need to push data.
    """
    bridge = get_webhook_bridge()
    if not bridge.verify_inbound(x_saphira_automation_key):
        raise HTTPException(status_code=401, detail="Invalid or missing automation key")

    target = body.target.lower().strip()
    if target == "zapier":
        return bridge.trigger_zapier(body.payload)
    if target == "make":
        return bridge.trigger_make(body.payload)
    if target == "n8n_cross_post":
        return bridge.trigger_cross_post(body.payload)
    if target == "n8n_onboarding":
        if not body.email:
            raise HTTPException(status_code=400, detail="email required for onboarding")
        return bridge.trigger_onboarding(body.email, body.tier or "free")
    if target == "revenue":
        return bridge.sync_revenue_event(
            event_type=body.payload.get("event_type", "manual"),
            amount=body.payload.get("amount"),
            currency=body.payload.get("currency", "USD"),
            source=body.payload.get("source", "saphira"),
            metadata=body.payload.get("metadata"),
        )
    if target == "broadcast":
        return bridge.broadcast(body.payload)

    raise HTTPException(status_code=400, detail=f"Unknown target: {body.target}")


@router.get("/health")
async def webhooks_health():
    bridge = get_webhook_bridge()
    return {
        "status": "ok",
        "outbound": {
            "n8n_cross_post": bool(bridge.n8n_cross_post),
            "n8n_onboarding": bool(bridge.n8n_onboarding),
            "n8n_revenue": bool(bridge.n8n_revenue),
            "make": bool(bridge.make_webhook),
            "zapier": bool(bridge.zapier_hook),
            "generic_count": len(bridge.generic_hooks),
        },
        "inbound_secret_configured": bool(bridge.inbound_secret),
    }
