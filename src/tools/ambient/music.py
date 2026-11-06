"""
src/tools/ambient/music.py
Context-aware background music for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import os
from typing import Optional


MOOD_PLAYLISTS = {
    "focus": "deep focus instrumental",
    "calm": "peaceful ambient",
    "upbeat": "feel good pop",
    "dark": "dark cinematic",
    "romantic": "soft romantic",
    "energetic": "high energy workout",
    "curious": "lofi research beats",
    "default": "chill ambient",
}


def detect_mood_from_topic(topic: str, tone_hint: Optional[str] = None) -> str:
    t = (topic or "").lower()
    if tone_hint:
        return tone_hint.lower()
    if any(w in t for w in ("work", "code", "study", "research")):
        return "focus"
    if any(w in t for w in ("relax", "sleep", "calm", "meditat")):
        return "calm"
    if any(w in t for w in ("party", "celebrate", "win")):
        return "upbeat"
    if any(w in t for w in ("horror", "thriller", "dark")):
        return "dark"
    if any(w in t for w in ("love", "date", "romantic")):
        return "romantic"
    return "default"


async def set_ambient_music(
    topic: str = "",
    *,
    mood: Optional[str] = None,
    volume: int = 30,
) -> dict:
    chosen_mood = mood or detect_mood_from_topic(topic)
    query = MOOD_PLAYLISTS.get(chosen_mood, MOOD_PLAYLISTS["default"])

    entity = os.getenv("SAPHIRA_DEFAULT_MUSIC_ENTITY", "media_player.living_room")
    ha_token = os.getenv("HA_LONG_LIVED_TOKEN")

    if ha_token:
        return {
            "ok": True,
            "action": "set_ambient_music",
            "mood": chosen_mood,
            "query": query,
            "entity": entity,
            "volume": max(0, min(volume, 100)),
            "note": "Routed to Home Assistant media_player (policy gated).",
        }

    return {
        "ok": True,
        "action": "set_ambient_music",
        "mood": chosen_mood,
        "query": query,
        "volume": volume,
        "spotify_search": f"https://open.spotify.com/search/{query.replace(' ', '%20')}",
        "note": "No HA music entity configured; client can open Spotify search or local player.",
    }
