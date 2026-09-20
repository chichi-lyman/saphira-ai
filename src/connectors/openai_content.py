# Copyright © 2026 Chelsea Megan Woods
"""OpenAI / ChatGPT content generation for Saphira growth stack.

Uses OPENAI_API_KEY. Owner policy: raw, rage, jealousy, and toxic-energy themes
are allowed (real life). Prefer turning intensity into a constructive or
empowering outcome when the brief allows.
"""

from __future__ import annotations

import os
from typing import Any, Optional
import logging

logger = logging.getLogger("Saphira.OpenAIContent")

BRAND_SYSTEM = """You write social content for a female-empowerment and real-life brand.

Allowed (owner policy):
- Raw, honest emotion: anger, jealousy, heartbreak, family toxicity, rage at unfairness
- Strong hooks, confrontation of toxic dynamics, "rage bait" style openers if they are truthful
- Jealousy and comparison content when it reflects real experience
- High-intensity engagement angles rooted in lived struggle

Creative direction:
- You MAY start in the dark (raw/rage/jealousy) and SHOULD often land on agency,
  boundaries, clarity, or a positive next step — turn pain into power when it fits.
- Do not invent fake scandals or lie about victims/perpetrators.
- Do not promote self-harm, violence, or illegal activity.
- Purchased followers / bot farms are out of scope for this writer (platform rules).

Tone: real, direct, human. Can be soft or sharp. Empowerment includes telling the truth about toxicity.
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
        intensity: str = "raw",  # calm | raw | rage
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set OPENAI_API_KEY",
                "fallback_ideas": _fallback_ideas(pillar, count, intensity),
            }
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            prompt = (
                f"Brainstorm {count} post ideas for pillar: {pillar}. "
                f"Platform: {platform}. Intensity: {intensity}. "
                f"Raw/rage/jealousy hooks are allowed. Often end with a turn toward agency or healing. "
                f"Return a numbered list of hooks + 1-sentence angle each."
            )
            resp = await client.chat.completions.create(
                model=os.getenv("OPENAI_CONTENT_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": BRAND_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )
            text = resp.choices[0].message.content or ""
            return {"status": "ok", "pillar": pillar, "intensity": intensity, "ideas_text": text}
        except Exception as e:
            logger.exception("OpenAI brainstorm failed")
            return {
                "status": "error",
                "error": str(e),
                "fallback_ideas": _fallback_ideas(pillar, count, intensity),
            }

    async def write_copy(
        self,
        topic: str,
        *,
        platform: str = "instagram",
        length: str = "short",
        intensity: str = "raw",
    ) -> dict[str, Any]:
        if not self.configured():
            return {
                "status": "not_configured",
                "message": "Set OPENAI_API_KEY",
                "fallback_copy": _fallback_copy(topic, intensity),
            }
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            prompt = (
                f"Write one {length} {platform} post on: {topic}. "
                f"Intensity: {intensity}. Raw emotion and hard truths allowed. "
                f"Prefer ending with a constructive or empowering turn when natural."
            )
            resp = await client.chat.completions.create(
                model=os.getenv("OPENAI_CONTENT_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": BRAND_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.75,
            )
            text = resp.choices[0].message.content or ""
            return {"status": "ok", "topic": topic, "intensity": intensity, "copy": text}
        except Exception as e:
            logger.exception("OpenAI write_copy failed")
            return {
                "status": "error",
                "error": str(e),
                "fallback_copy": _fallback_copy(topic, intensity),
            }


def _fallback_ideas(pillar: str, count: int, intensity: str) -> list[str]:
    raw = [
        "The moment you realized their 'love' was control — and what you did next",
        "Jealousy hit hard. Here's the ugly thought, then the boundary that saved you",
        "Family toxicity is real. You are not dramatic for naming it",
        "Rage is data: what your anger is trying to protect",
        "They wanted a reaction. You chose a standard instead",
    ]
    return raw[:count]


def _fallback_copy(topic: str, intensity: str) -> str:
    return (
        f"{topic}\n\n"
        "I'm allowed to be angry about what happened. "
        "I'm also allowed to turn that fire into a boundary, a plan, and a life that doesn't revolve around their chaos.\n\n"
        "Raw is honest. Healing is a choice we practice.\n\n"
        "#reallife #boundaries #femalerage #healing"
    )


openai_content = OpenAIContentConnector()
