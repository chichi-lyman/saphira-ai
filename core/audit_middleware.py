from __future__ import annotations

import logging
import os
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from storage.database import AsyncSessionFactory

logger = logging.getLogger("saphira.audit")


class AuditEventMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return response
        if AsyncSessionFactory is None:
            logger.warning("Audit skipped: DATABASE_URL is not configured")
            return response
        tenant_id = getattr(request.state, "tenant_id", None) or request.headers.get("X-Tenant-ID", "unknown")
        actor_did = getattr(request.state, "actor_did", None) or request.headers.get("X-Agent-DID", "did:saphira:system:anonymous")
        client_ip = request.client.host if request.client else "0.0.0.0"
        payload = {
            "status_code": response.status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "query_params": dict(request.query_params),
        }
        try:
            async with AsyncSessionFactory() as session:
                async with session.begin():
                    await session.execute(
                        text("""
                            INSERT INTO audit_events
                            (tenant_id, actor_did, action, resource, payload_json, ip_address)
                            VALUES (:tenant_id, :actor_did, :action, :resource, CAST(:payload_json AS jsonb), :ip_address)
                        """),
                        {
                            "tenant_id": tenant_id,
                            "actor_did": actor_did,
                            "action": f"{request.method}:{request.url.path}",
                            "resource": request.url.path,
                            "payload_json": __import__("json").dumps(payload),
                            "ip_address": client_ip,
                        },
                    )
        except Exception:
            logger.exception("Failed to write audit event")
        return response
