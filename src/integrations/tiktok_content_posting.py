"""TikTok Content Posting API integration for Saphira.

Server-side only. OAuth tokens are persisted in Redis and never exposed to the
browser. This module follows TikTok's OAuth v2 + Content Posting API flow.
"""

from __future__ import annotations

import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any

import httpx
from redis.asyncio import Redis

TIKTOK_AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"


class TikTokConfigError(RuntimeError):
    pass


class TikTokAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass
class TikTokToken:
    open_id: str
    access_token: str
    refresh_token: str
    access_expires_at: int
    refresh_expires_at: int
    scope: str
    token_type: str = "Bearer"

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TikTokToken":
        now = int(time.time())
        return cls(
            open_id=payload["open_id"],
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"],
            access_expires_at=now + int(payload.get("expires_in", 86400)),
            refresh_expires_at=now + int(payload.get("refresh_expires_in", 31536000)),
            scope=payload.get("scope", ""),
            token_type=payload.get("token_type", "Bearer"),
        )

    @classmethod
    def from_json(cls, raw: str) -> "TikTokToken":
        return cls(**json.loads(raw))

    def to_json(self) -> str:
        return json.dumps(self.__dict__)


class TikTokContentPostingService:
    def __init__(self) -> None:
        self.client_key = os.getenv("TIKTOK_CLIENT_KEY", "")
        self.client_secret = os.getenv("TIKTOK_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("TIKTOK_REDIRECT_URI", "")
        self.redis_url = os.getenv("REDIS_URL", "")
        if not self.client_key or not self.client_secret or not self.redirect_uri:
            raise TikTokConfigError(
                "TikTok is not configured. Set TIKTOK_CLIENT_KEY, "
                "TIKTOK_CLIENT_SECRET and TIKTOK_REDIRECT_URI."
            )
        if not self.redis_url:
            raise TikTokConfigError("REDIS_URL is required for persistent TikTok OAuth sessions.")

    def redis(self) -> Redis:
        return Redis.from_url(self.redis_url, decode_responses=True)

    async def create_oauth_state(self) -> str:
        state = secrets.token_urlsafe(32)
        async with self.redis() as redis:
            await redis.setex(f"saphira:tiktok:oauth:{state}", 600, "1")
        return state

    async def consume_oauth_state(self, state: str) -> bool:
        async with self.redis() as redis:
            key = f"saphira:tiktok:oauth:{state}"
            exists = await redis.get(key)
            if exists is None:
                return False
            await redis.delete(key)
            return True

    def authorization_url(self, state: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_key": self.client_key,
            "response_type": "code",
            "scope": "video.publish,user.info.basic",
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        return f"{TIKTOK_AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> TikTokToken:
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                TIKTOK_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"},
            )
        payload = response.json()
        if response.status_code >= 400 or payload.get("error"):
            raise TikTokAPIError(payload.get("error_description") or "TikTok OAuth exchange failed", response.status_code, payload)
        token = TikTokToken.from_payload(payload)
        await self.save_token(token)
        return token

    async def save_token(self, token: TikTokToken) -> None:
        ttl = max(60, token.refresh_expires_at - int(time.time()))
        async with self.redis() as redis:
            await redis.setex(f"saphira:tiktok:token:{token.open_id}", ttl, token.to_json())

    async def load_token(self, open_id: str) -> TikTokToken | None:
        async with self.redis() as redis:
            raw = await redis.get(f"saphira:tiktok:token:{open_id}")
        return TikTokToken.from_json(raw) if raw else None

    async def get_valid_token(self, open_id: str) -> TikTokToken:
        token = await self.load_token(open_id)
        if not token:
            raise TikTokAPIError("TikTok account is not connected.", 401)
        if token.access_expires_at - int(time.time()) > 300:
            return token

        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                TIKTOK_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"},
            )
        payload = response.json()
        if response.status_code >= 400 or payload.get("error"):
            raise TikTokAPIError(payload.get("error_description") or "TikTok token refresh failed", response.status_code, payload)
        refreshed = TikTokToken.from_payload(payload)
        await self.save_token(refreshed)
        return refreshed

    async def creator_info(self, open_id: str) -> dict[str, Any]:
        token = await self.get_valid_token(open_id)
        return await self._post("/post/publish/creator_info/query/", token.access_token, {})

    async def direct_post_video(
        self,
        open_id: str,
        *,
        video_url: str,
        title: str,
        privacy_level: str = "PUBLIC_TO_EVERYONE",
        disable_comment: bool = False,
        disable_duet: bool = False,
        disable_stitch: bool = False,
        video_cover_timestamp_ms: int = 0,
    ) -> dict[str, Any]:
        token = await self.get_valid_token(open_id)
        creator = await self.creator_info(open_id)
        options = creator.get("privacy_level_options", [])
        if privacy_level not in options:
            raise TikTokAPIError(f"Privacy level {privacy_level!r} is not allowed for this creator.", 400, creator)

        payload = {
            "post_info": {
                "title": title[:2200],
                "privacy_level": privacy_level,
                "disable_comment": disable_comment,
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": max(0, int(video_cover_timestamp_ms)),
            },
            "source_info": {"source": "PULL_FROM_URL", "video_url": video_url},
        }
        return await self._post("/post/publish/video/init/", token.access_token, payload)

    async def publish_status(self, open_id: str, publish_id: str) -> dict[str, Any]:
        token = await self.get_valid_token(open_id)
        return await self._post("/post/publish/status/fetch/", token.access_token, {"publish_id": publish_id})

    async def disconnect(self, open_id: str) -> None:
        async with self.redis() as redis:
            await redis.delete(f"saphira:tiktok:token:{open_id}")

    async def _post(self, path: str, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{TIKTOK_API_BASE}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
            )
        body = response.json()
        error = body.get("error", {})
        if response.status_code >= 400 or error.get("code") not in (None, "ok"):
            raise TikTokAPIError(error.get("message") or "TikTok API request failed", response.status_code, body)
        return body.get("data", body)
