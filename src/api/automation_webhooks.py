"""Secure, provider-neutral automation webhooks for Make.com and Zapier.

Inbound events are authenticated, deduplicated, and appended to a Redis Stream.
Outbound events are delivered to a configured automation catch-hook.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Literal

import httpx
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from redis.asyncio import Redis

from src.config.settings import get_settings

logger = logging.getLogger("saphira.automation")
router = APIRouter(prefix="/api/integrations/automation", tags=["automation-webhooks"])

_ALLOWED_EVENTS = {
    "lead.created",
    "lead.qualified",
    "lead.opted_out",
    "order.paid",
    "order.refunded",
    "order.fulfilled",
    "content.metrics.updated",
    "automation.test",
}
_redis: Redis | None = None


class AutomationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=8, max_length=128)
    event_type: str
    source: Literal["make", "zapier", "saphira", "shopify", "metricool"]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str | None = Field(default=None, max_length=128)
    correlation_id: str | None = Field(default=None, max_length=128)
    data: dict[str, Any] = Field(default_factory=dict)


def _authorized(provided: str | None, expected: str | None) -> bool:
    return bool(provided and expected and hmac.compare_digest(provided, expected))


async def _redis_client() -> Redis:
    global _redis
    settings = get_settings()
    if not settings.redis_url:
        raise HTTPException(status_code=503, detail="Automation event store is not configured")
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await _redis.ping()
    except Exception as exc:
        logger.warning("automation_store_unavailable error_type=%s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Automation event store unavailable") from exc
    return _redis


@router.get("/health")
async def automation_health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "enabled": bool(settings.automation_webhook_secret),
        "inbound_auth_configured": bool(settings.automation_webhook_secret),
        "outbound_configured": bool(settings.automation_outbound_url),
        "durable_store_configured": bool(settings.redis_url),
        "providers": ["make", "zapier"],
    }


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def receive_automation_event(
    event: AutomationEvent,
    automation_key: str | None = Header(default=None, alias="X-Saphira-Automation-Key"),
) -> dict[str, Any]:
    """Accept an event from Make/Zapier; dedupe and persist it to a Redis Stream."""
    settings = get_settings()
    if not _authorized(automation_key, settings.automation_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid automation credentials")
    if event.event_type not in _ALLOWED_EVENTS:
        raise HTTPException(status_code=422, detail="Unsupported event_type")

    client = await _redis_client()
    digest = hashlib.sha256(event.event_id.encode("utf-8")).hexdigest()
    dedupe_key = f"saphira:automation:seen:{digest}"
    claimed = await client.set(dedupe_key, "1", nx=True, ex=86400)
    if not claimed:
        return {"accepted": True, "duplicate": True, "event_id": event.event_id}

    stream = "saphira:automation:inbox"
    payload = event.model_dump(mode="json")
    try:
        stream_id = await client.xadd(
            stream,
            {"event_id": event.event_id, "event_type": event.event_type,
             "payload": json.dumps(payload, separators=(",", ":"))},
            maxlen=10000,
            approximate=True,
        )
    except Exception as exc:
        await client.delete(dedupe_key)
        logger.error("automation_event_persist_failed event_type=%s", event.event_type)
        raise HTTPException(status_code=503, detail="Event persistence failed; retry safely") from exc

    logger.info("automation_event_accepted event_type=%s stream_id=%s", event.event_type, stream_id)
    return {"accepted": True, "duplicate": False, "event_id": event.event_id, "stream_id": stream_id}


async def publish_automation_event(
    event_type: str,
    data: dict[str, Any],
    *,
    event_id: str,
    source: str = "saphira",
    tenant_id: str | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Send a Saphira domain event to the configured Make/Zapier catch-hook."""
    if event_type not in _ALLOWED_EVENTS:
        raise ValueError(f"Unsupported automation event type: {event_type}")
    url = get_settings().automation_outbound_url
    if not url:
        return {"delivered": False, "reason": "outbound_not_configured"}

    event = AutomationEvent(
        event_id=event_id,
        event_type=event_type,
        source=source,  # type: ignore[arg-type]
        occurred_at=datetime.now(timezone.utc),
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        data=data,
    )
    body = event.model_dump(mode="json")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0)) as client:
            response = await client.post(url, json=body, headers={"Idempotency-Key": event_id})
            response.raise_for_status()
        return {"delivered": True, "status_code": response.status_code, "event_id": event_id}
    except httpx.HTTPError as exc:
        logger.warning("automation_event_delivery_failed event_type=%s error_type=%s",
                       event_type, type(exc).__name__)
        return {"delivered": False, "reason": "delivery_failed", "event_id": event_id}


@router.post("/test")
async def send_test_event(
    automation_key: str | None = Header(default=None, alias="X-Saphira-Automation-Key"),
) -> dict[str, Any]:
    """Authenticated connectivity check; no customer or order data is emitted."""
    settings = get_settings()
    if not _authorized(automation_key, settings.automation_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid automation credentials")
    return await publish_automation_event(
        "automation.test",
        {"message": "Saphira automation connection test", "sent_at": time.time()},
        event_id=f"test-{int(time.time())}",
    )
