# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Meta Graph API Facebook Page connector for Saphira AI.

Capabilities (when long-lived Page access token + required scopes are present):
- Scheduled text / link posts
- Photo & media uploads to the Page feed
- Comment reading, auto-reply drafting, and moderation (hide/flag)
- Basic Messenger conversation handling (when messaging permissions granted)
- Page insights (reach, impressions, reactions, follower growth)

Required env:
  FACEBOOK_ACCESS_TOKEN  — long-lived Page access token
  FACEBOOK_PAGE_ID       — numeric Page ID

Optional:
  FACEBOOK_GRAPH_VERSION (default v19.0)
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


class FacebookConnector:
    def __init__(self) -> None:
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "").strip()
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "").strip()
        self.graph_version = os.getenv("FACEBOOK_GRAPH_VERSION", "v19.0").strip()
        self.base = f"https://graph.facebook.com/{self.graph_version}"

    def _ready(self) -> bool:
        return bool(self.access_token and self.page_id)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._ready():
            return {"status": "error", "message": "Facebook credentials missing"}
        p = dict(params or {})
        p["access_token"] = self.access_token
        url = f"{self.base}/{path.lstrip('/')}"
        try:
            r = requests.get(url, params=p, timeout=25)
            data = r.json()
            if r.status_code >= 400:
                return {"status": "error", "http_status": r.status_code, "data": data}
            return {"status": "ok", "data": data}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def _post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._ready():
            return {"status": "error", "message": "Facebook credentials missing"}
        payload = dict(data or {})
        payload["access_token"] = self.access_token
        url = f"{self.base}/{path.lstrip('/')}"
        try:
            r = requests.post(url, data=payload, timeout=30)
            body = r.json()
            if r.status_code >= 400:
                return {"status": "error", "http_status": r.status_code, "data": body}
            return {"status": "ok", "data": body}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    # -------------------------------------------------------------------------
    # 1. Automated Content Creation & Publishing
    # -------------------------------------------------------------------------

    def post(
        self,
        message: str,
        link: Optional[str] = None,
        scheduled_publish_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Publish a text (or link) post. Optionally schedule via Unix timestamp."""
        payload: Dict[str, Any] = {"message": message}
        if link:
            payload["link"] = link
        if scheduled_publish_time:
            payload["published"] = "false"
            payload["scheduled_publish_time"] = int(scheduled_publish_time)
        return self._post(f"{self.page_id}/feed", payload)

    def upload_photo(
        self,
        image_url: str,
        caption: Optional[str] = None,
        published: bool = True,
    ) -> Dict[str, Any]:
        """Upload a photo to the Page (URL-based)."""
        payload: Dict[str, Any] = {
            "url": image_url,
            "published": "true" if published else "false",
        }
        if caption:
            payload["caption"] = caption
        return self._post(f"{self.page_id}/photos", payload)

    def schedule_post(
        self,
        message: str,
        unix_timestamp: int,
        link: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience wrapper for scheduled text posts."""
        return self.post(message, link=link, scheduled_publish_time=unix_timestamp)

    # -------------------------------------------------------------------------
    # 2. Audience Engagement & Moderation
    # -------------------------------------------------------------------------

    def get_comments(self, post_id: str, limit: int = 25) -> Dict[str, Any]:
        """List comments on a public post."""
        return self._get(f"{post_id}/comments", {"limit": limit, "filter": "stream"})

    def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Post a reply to a comment (uses Page voice)."""
        return self._post(f"{comment_id}/comments", {"message": message})

    def hide_comment(self, comment_id: str, hide: bool = True) -> Dict[str, Any]:
        """Hide or unhide a comment (moderation)."""
        return self._post(f"{comment_id}", {"is_hidden": "true" if hide else "false"})

    def get_conversations(self, limit: int = 10) -> Dict[str, Any]:
        """List recent Messenger conversations (requires pages_messaging)."""
        return self._get(f"{self.page_id}/conversations", {"limit": limit})

    def send_messenger_message(self, recipient_id: str, message: str) -> Dict[str, Any]:
        """Send a basic text message via Messenger Platform."""
        # Graph API uses /me/messages with a Page token; recipient is PSID.
        payload = {
            "recipient": f'{{"id":"{recipient_id}"}}',
            "message": f'{{"text":"{message}"}}',
            "messaging_type": "RESPONSE",
        }
        return self._post("me/messages", payload)

    # -------------------------------------------------------------------------
    # 3. Analytics & Growth Optimization
    # -------------------------------------------------------------------------

    def get_page_insights(
        self,
        metrics: Optional[List[str]] = None,
        period: str = "day",
    ) -> Dict[str, Any]:
        """Pull Page-level insights (reach, impressions, engagement, etc.)."""
        default_metrics = [
            "page_impressions",
            "page_impressions_unique",
            "page_engaged_users",
            "page_post_engagements",
            "page_fans",
            "page_fan_adds",
        ]
        metric_str = ",".join(metrics or default_metrics)
        return self._get(
            f"{self.page_id}/insights",
            {"metric": metric_str, "period": period},
        )

    def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Insights for a single post."""
        metrics = "post_impressions,post_impressions_unique,post_engaged_users,post_reactions_by_type_total"
        return self._get(f"{post_id}/insights", {"metric": metrics})

    def list_recent_posts(self, limit: int = 10) -> Dict[str, Any]:
        """List recent published posts (for optimization loops)."""
        return self._get(
            f"{self.page_id}/published_posts",
            {"limit": limit, "fields": "id,message,created_time,permalink_url,shares,reactions.summary(true)"},
        )

    def health(self) -> Dict[str, Any]:
        if not self._ready():
            return {
                "status": "not_configured",
                "message": "Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID",
            }
        me = self._get(self.page_id, {"fields": "id,name,fan_count"})
        return {
            "status": "ready" if me.get("status") == "ok" else "error",
            "provider": "facebook_graph",
            "page": me.get("data"),
        }
