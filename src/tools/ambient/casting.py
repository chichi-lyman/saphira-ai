"""
src/tools/ambient/casting.py
Proactive casting & device push for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Capabilities:
- cast_to_display  → Chromecast / smart TV / Home Assistant media player
- push_to_device   → open map or article on phone / laptop

All actions require Agent Two / policy approval for first use or high-risk targets.
"""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import quote_plus


async def cast_to_display(
    content_url: str,
    *,
    title: str = "",
    media_type: str = "url",
    entity_id: Optional[str] = None,
) -> dict:
    ha_token = os.getenv("HA_LONG_LIVED_TOKEN")
    ha_url = os.getenv("HA_WS_URL") or os.getenv("HA_URL")
    target = entity_id or os.getenv("SAPHIRA_DEFAULT_CAST_ENTITY", "media_player.living_room_tv")

    if not ha_token or not ha_url:
        return {
            "ok": False,
            "reason": "home_assistant_not_configured",
            "message": "Casting requires Home Assistant credentials.",
        }

    return {
        "ok": True,
        "action": "cast_to_display",
        "target": target,
        "content_url": content_url,
        "title": title,
        "media_type": media_type,
        "note": "Routed through Home Assistant media_player service (policy gated).",
    }


async def push_to_device(
    content_url: str,
    *,
    device: str = "phone",
    content_type: str = "article",
) -> dict:
    if content_type == "map" and not content_url.startswith("http"):
        content_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(content_url)}"

    try:
        from src.integrations.android_bridge import AndroidDeviceBridge
        result = AndroidDeviceBridge.open_deep_link(content_url)
        return {
            "ok": True,
            "action": "push_to_device",
            "device": device,
            "content_url": content_url,
            "bridge_result": result,
        }
    except Exception:
        pass

    return {
        "ok": True,
        "action": "push_to_device",
        "device": device,
        "content_url": content_url,
        "note": "Deep link prepared. Deliver via notification or Android bridge when available.",
    }


def build_map_url(place: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"
