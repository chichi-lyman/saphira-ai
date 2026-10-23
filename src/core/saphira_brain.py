# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# SaphiraBrain — the single explicit connection between Saphira and her models.
# Every call injects the locked persona + competitive directive so the product
# stays character-first while still routing across strong frontier backends.

from __future__ import annotations

import logging
from typing import Any, Optional

from src.core.saphira_persona import SAMANTHA_PERSONA_PROMPT
from src.core.saphira_competitive_directive import competitive_system_suffix
from src.providers import get_provider_registry, GenerateRequest, GenerateResult

logger = logging.getLogger("SaphiraBrain")


def _build_system(extra: Optional[str] = None) -> str:
    """Persona + competitive positioning. Never generic."""
    base = SAMANTHA_PERSONA_PROMPT + competitive_system_suffix()
    if extra and extra.strip():
        return base + "\n\n[SESSION / TASK CONTEXT]\n" + extra.strip()
    return base


class SaphiraBrain:
    """
    Unified brain entry point for Saphira.

    - Always injects the Samantha-style persona and the persona-first competitive directive.
    - Routes through the multi-provider registry (Gemini → Claude → OpenAI → xAI by preference).
    - Falls back cleanly when a provider is down or unconfigured.
    - Does not claim to out-scale the frontier labs on raw general intelligence.
    """

    def __init__(self) -> None:
        self._registry = get_provider_registry()

    def health(self) -> dict[str, Any]:
        return {
            "brain": "SaphiraBrain",
            "persona_locked": True,
            "competitive_directive": True,
            "providers": self._registry.health(),
        }

    async def think(
        self,
        user_text: str,
        *,
        system_extra: Optional[str] = None,
        preferred: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> GenerateResult:
        """
        Core reasoning call. Returns a GenerateResult with status/text/provider.
        """
        system = _build_system(system_extra)
        req = GenerateRequest(
            prompt=user_text,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata or {"surface": "brain"},
        )
        result = await self._registry.generate(req, preferred=preferred, fallback=True)
        if result.status != "success":
            logger.warning(
                "brain_call_failed status=%s provider=%s message=%s",
                result.status,
                result.provider,
                result.message,
            )
        return result

    async def reply(
        self,
        user_text: str,
        *,
        conversation_context: Optional[str] = None,
        preferred: Optional[str] = None,
    ) -> Optional[str]:
        """Convenience: return only the text, or None on failure."""
        result = await self.think(
            user_text,
            system_extra=conversation_context,
            preferred=preferred,
            metadata={"surface": "chat"},
        )
        if result.status == "success" and result.text:
            return result.text.strip()
        return None


_brain: Optional[SaphiraBrain] = None


def get_saphira_brain() -> SaphiraBrain:
    global _brain
    if _brain is None:
        _brain = SaphiraBrain()
    return _brain
