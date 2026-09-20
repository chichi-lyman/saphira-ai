# Copyright © 2026 Chelsea Megan Woods
"""OpenAI / ChatGPT content generation for Saphira growth stack.

Uses OPENAI_API_KEY. Content must follow brand rules: empowerment, boundaries,
no rage-bait, no jealousy clickbait, no toxic engagement farming.
"""

from __future__ import annotations

import os
from typing import Any, Optional
import logging

logger = logging.getLogger("Saphira.OpenAIContent")

BRAND_SYSTEM = """You write social content for a female-empowerment brand.
Rules (non-negotiable):
- Focus: healthy boundaries, toxic relationship dynamics, self-confidence, resilience,
  positive energy, constructive handling of jealousy, toxic family and boundaries.
- Tone: warm, clear, grounded, respectful. Never condescending.
- Forbidden: rage-bait, jealousy clickbait, shaming, fear-mongering, "us vs them" pile-ons,
  manufactured outrage, misleading hooks that exploit pain without offering agency.
- Prefer practical takeaways, reflective questions, and hopeful next steps.
- Keep posts platform-ready (short paragraphs, optional soft CTA to resources).
"""


class OpenAIContentConnector:
    name = "openai_content"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def configured(self) -> bool:
        return bool(self.api_key)

    async def brainstorm(
        self,
        pillar: str,
        *,
        count: int = 5,
        platform: str = "instagram",
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set OPENAI_API_KEY",
                "fallback_ideas": _fallback_ideas(pillar, count),
            }
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            prompt = (
                f"Brainstorm {count} post ideas for pillar: {pillar}. "
                f"Platform: {platform}. Return a numbered list of hooks + 1-sentence angle each."
            )
            resp = await client.chat.completions.create(
                model=os.getenv("OPENAI_CONTENT_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": BRAND_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            text = resp.choices[0].message.content or ""
            return {"status": "ok", "pillar": pillar, "ideas_text": text}
        except Exception as e:
            logger.exception("OpenAI brainstorm failed")
            return {"status": "error", "error": str(e), "fallback_ideas": _fallback_ideas(pillar, count)}

    async def write_copy(
        self,
        topic: str,
        *,
        platform: str = "instagram",
        length: str = "short",
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set OPENAI_API_KEY",
                "fallback_copy": _fallback_copy(topic),
            }
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            prompt = (
                f"Write one {length} {platform} post on: {topic}. "
                "No hashtag spam; 3–5 relevant tags max at end optional."
            )
            resp = await client.chat.completions.create(
                model=os.getenv("OPENAI_CONTENT_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": BRAND_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            text = resp.choices[0].message.content or ""
            return {"status": "ok", "topic": topic, "copy": text}
        except Exception as e:
            logger.exception("OpenAI write_copy failed")
            return {"status": "error", "error": str(e), "fallback_copy": _fallback_copy(topic)}


def _fallback_ideas(pillar: str, count: int) -> list[str]:
    base = {
        "boundaries": [
            "A boundary is a door, not a wall — here's one sentence that protects your peace",
            "What to say when family guilt-trips your no",
            "Three signs your 'flexibility' is actually self-abandonment",
        ],
        "toxic_dynamics": [
            "Love should not require you to shrink — name one pattern to watch for",
            "When silence is safety vs when silence is avoidance",
            "How to leave a conversation that only drains you",
        ],
        "confidence": [
            "Confidence is a practice, not a personality type",
            "One small promise to yourself this week",
            "Rebuilding trust with yourself after people-pleasing",
        ],
    }
    key = "boundaries"
    pl = pillar.lower()
    if "toxic" in pl or "relationship" in pl:
        key = "toxic_dynamics"
    elif "confidence" in pl or "resilien" in pl:
        key = "confidence"
    ideas = base.get(key, base["boundaries"])
    return ideas[:count]


def _fallback_copy(topic: str) -> str:
    return (
        f"{topic}\n\n"
        "You are allowed to protect your energy without explaining every decision.\n"
        "Start with one clear boundary this week. You do not need permission to be at peace.\n\n"
        "#boundaries #selftrust #femaleempowerment"
    )


openai_content = OpenAIContentConnector()
