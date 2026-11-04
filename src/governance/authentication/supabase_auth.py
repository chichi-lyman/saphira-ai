"""Validate Supabase-issued access tokens and expose a trusted request identity."""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any
import httpx
from fastapi import Header, HTTPException, status

@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None
    app_metadata: dict[str, Any]

async def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    """Resolve the bearer token through Supabase Auth's authoritative user API."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="A valid sign-in session is required",
                            headers={"WWW-Authenticate": "Bearer"})
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    supabase_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    publishable_key = (os.getenv("SUPABASE_PUBLISHABLE_KEY") or
                       os.getenv("SUPABASE_ANON_KEY") or "").strip()
    if not supabase_url or not publishable_key:
        raise HTTPException(status_code=503, detail="Supabase Auth is not configured on this service")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                supabase_url + "/auth/v1/user",
                headers={"apikey": publishable_key, "Authorization": "Bearer " + token},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=503, detail="Identity provider timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Identity provider is unavailable") from exc
    if response.status_code in (401, 403):
        raise HTTPException(status_code=401, detail="Sign-in session is invalid or expired",
                            headers={"WWW-Authenticate": "Bearer"})
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="Identity provider is unavailable")
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Could not validate sign-in session")
    try:
        payload = response.json()
        user_id = str(payload["id"])
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Identity provider returned an invalid identity") from exc
    return AuthenticatedUser(id=user_id, email=payload.get("email"),
                             app_metadata=payload.get("app_metadata") or {})
