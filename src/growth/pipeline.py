# Copyright © 2026 Chelsea Megan Woods
"""Growth pipeline: pillar → ChatGPT copy → Publer/FeedHive schedule.

Instinct/Apex policy: ALLOW (owner). Still requires API secrets to actually publish.
"""

from __future__ import annotations

from typing import Any, Optional
import logging

from src.growth.content_pillars import CONTENT_PILLARS, growth_principles
from src.connectors.openai_content import openai_content
from src.connectors.publer import publer
from src.connectors.feedhive import feedhive

logger = logging.getLogger("Saphira.GrowthPipeline")


async def run_content_cycle(
    *,
    pillar_id: Optional[str] = None,
    topic: Optional[str] = None,
    platform: str = "instagram",
    scheduler: str = "feedhive",  # feedhive | publer | both
    scheduled_at: Optional[str] = None,
    publish: bool = True,
) -> dict[str, Any]:
    principles = growth_principles()
    pillar = None
    if pillar_id:
        pillar = next((p for p in CONTENT_PILLARS if p["id"] == pillar_id), None)
    topic = topic or (pillar["example_angles"][0] if pillar else "healthy boundaries")

    ideas = await openai_content.brainstorm(
        pillar["title"] if pillar else topic, count=3, platform=platform
    )
    copy_result = await openai_content.write_copy(topic, platform=platform, length="short")
    text = copy_result.get("copy") or copy_result.get("fallback_copy") or topic

    schedule_results: dict[str, Any] = {}
    if publish:
        if scheduler in ("feedhive", "both"):
            schedule_results["feedhive"] = await feedhive.schedule_post(
                text=text, scheduled=scheduled_at
            )
        if scheduler in ("publer", "both"):
            schedule_results["publer"] = await publer.schedule_post(
                text=text, scheduled_at=scheduled_at
            )

    return {
        "status": "ok",
        "policy": "ALLOW",
        "agents": ["agent_instinct", "agent_apex"],
        "principles": principles,
        "pillar": pillar,
        "topic": topic,
        "ideas": ideas,
        "copy": copy_result,
        "schedule": schedule_results,
        "note": "Configure OPENAI_API_KEY, FEEDHIVE_TRIGGER_URL, PUBLER_API_TOKEN for live publish",
    }
