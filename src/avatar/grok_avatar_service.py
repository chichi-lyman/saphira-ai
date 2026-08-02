# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Saphira Visual Avatar — Grok Imagine pipeline
# Anchored on Chelsea Megan Woods' likeness for public-facing assistant UI.

from __future__ import annotations

import os
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SaphiraAvatar")

# Master visual anchors — derived from Chelsea's reference photos
CHELSEA_VISUAL_DNA = (
    "Chelsea Megan Woods as Saphira AI assistant, "
    "platinum blonde hair with dark black under-layers, "
    "long wavy ombré hair, striking blue-grey eyes, "
    "full lashes, septum piercing, gold layered cross necklaces, "
    "detailed chest tattoo with wings and cross motif, "
    "wearing elegant black corset top, "
    "confident warm direct gaze, soft duck-face or gentle smile, "
    "high-end clean ivory white background, "
    "sleek holographic neon electric blue and ultraviolet aura, "
    "classy light-mode sci-fi cyberpunk-girly aesthetic, "
    "cinematic soft lighting, 2k quality, photorealistic"
)

STATE_PROMPTS: Dict[str, str] = {
    "idle": "calm poised posture, soft neutral expression, subtle holographic HUD rings floating around her",
    "welcome": "warm welcoming smile, one hand raised in a gentle greeting gesture, glowing holographic crystal near her palm",
    "talking": "mid-speech expression, lips slightly parted as if speaking, animated eyes, soft cyan voice-wave particles",
    "thinking": "thoughtful look slightly upward, fingers near chin, ultraviolet constellation particles orbiting",
    "listening": "attentive lean-in expression, soft electric-blue ear/halo glow, quiet focus",
    "glow": "radiant proud expression, full holographic bloom and ultraviolet light flare, celebratory energy",
    "confirm": "reassuring nod and soft smile, small holographic checkmark glyph near shoulder",
}


class AvatarState(str, Enum):
    IDLE = "idle"
    WELCOME = "welcome"
    TALKING = "talking"
    THINKING = "thinking"
    LISTENING = "listening"
    GLOW = "glow"
    CONFIRM = "confirm"


class GrokAvatarService:
    """
    Orchestrates Grok Imagine image-to-image and image-to-video
    for the Saphira public avatar, always anchored on Chelsea's look.
    """

    def __init__(self, api_key: Optional[str] = None, reference_image_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        self.reference_image_url = reference_image_url or os.getenv(
            "SAPHIRA_AVATAR_MASTER_URL",
            "",
        )
        self._client = None
        self._cache: Dict[str, str] = {}  # state -> last image url

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            logger.warning("No XAI_API_KEY — avatar generation will return prompt stubs only.")
            return None
        try:
            from openai import OpenAI

            self._client = OpenAI(
                base_url="https://api.x.ai/v1",
                api_key=self.api_key,
            )
            return self._client
        except Exception as e:
            logger.error("Failed to init xAI client: %s", e)
            return None

    def build_prompt(self, state: str | AvatarState, extra: str = "") -> str:
        key = state.value if isinstance(state, AvatarState) else state
        action = STATE_PROMPTS.get(key, STATE_PROMPTS["idle"])
        parts = [CHELSEA_VISUAL_DNA, action]
        if extra:
            parts.append(extra)
        return ". ".join(parts)

    def generate_frame(
        self,
        state: str | AvatarState = AvatarState.IDLE,
        extra_action: str = "",
        reference_url: Optional[str] = None,
        aspect_ratio: str = "9:16",
    ) -> Dict[str, Any]:
        """
        Generate a single avatar still via Grok Imagine (image quality / I2I).
        Returns structured result with url when live, or prompt package when offline.
        """
        key = state.value if isinstance(state, AvatarState) else state
        prompt = self.build_prompt(key, extra_action)
        ref = reference_url or self.reference_image_url

        client = self._get_client()
        if client is None:
            return {
                "status": "stub",
                "state": key,
                "prompt": prompt,
                "reference": ref or None,
                "url": self._cache.get(key),
                "message": "No XAI_API_KEY — returning prompt package. Set key for live Grok Imagine.",
                "owner": "Chelsea Megan Woods",
            }

        try:
            extra_body: Dict[str, Any] = {
                "aspect_ratio": aspect_ratio,
                "resolution": "2k",
            }
            if ref:
                extra_body["init_image"] = [ref]

            response = client.images.generate(
                model="grok-imagine-image-quality",
                prompt=prompt,
                extra_body=extra_body,
            )
            url = response.data[0].url if response.data else None
            if url:
                self._cache[key] = url
            return {
                "status": "ok",
                "state": key,
                "url": url,
                "prompt": prompt,
                "model": "grok-imagine-image-quality",
                "owner": "Chelsea Megan Woods",
            }
        except Exception as e:
            logger.exception("Avatar frame generation failed")
            return {
                "status": "error",
                "state": key,
                "error": str(e),
                "prompt": prompt,
                "message": "Grok Imagine call failed; see error.",
            }

    def generate_clip(
        self,
        state: str | AvatarState = AvatarState.TALKING,
        extra_action: str = "",
        reference_url: Optional[str] = None,
        duration_sec: int = 4,
    ) -> Dict[str, Any]:
        """
        Image-to-video style clip for talking / welcome / glow reactions.
        Uses grok-imagine video surface when available; otherwise returns
        a frame + motion intent for the client to animate.
        """
        key = state.value if isinstance(state, AvatarState) else state
        prompt = self.build_prompt(key, extra_action)
        ref = reference_url or self.reference_image_url or self._cache.get(key)

        client = self._get_client()
        if client is None:
            return {
                "status": "stub",
                "state": key,
                "prompt": prompt,
                "duration_sec": duration_sec,
                "reference": ref,
                "message": "No XAI_API_KEY — video stub. Client can pulse holographic UI on still.",
                "owner": "Chelsea Megan Woods",
            }

        # Prefer video model when the API surface supports it; fall back to still + motion tag
        try:
            # Attempt video generation surface (xAI Grok Imagine video)
            # If the deployed model name differs, still returns a useful package.
            extra_body: Dict[str, Any] = {
                "duration": duration_sec,
                "aspect_ratio": "9:16",
            }
            if ref:
                extra_body["init_image"] = [ref]

            # Some deployments expose video via images.generate with video model id
            response = client.images.generate(
                model="grok-imagine-video",
                prompt=prompt + ". Subtle natural motion, soft breathing, holographic particles drifting.",
                extra_body=extra_body,
            )
            url = response.data[0].url if response.data else None
            return {
                "status": "ok",
                "state": key,
                "url": url,
                "media_type": "video",
                "duration_sec": duration_sec,
                "prompt": prompt,
                "model": "grok-imagine-video",
                "owner": "Chelsea Megan Woods",
            }
        except Exception as e:
            logger.warning("Video path unavailable (%s); falling back to frame.", e)
            frame = self.generate_frame(state=key, extra_action=extra_action, reference_url=ref)
            frame["media_type"] = "image"
            frame["motion_hint"] = key
            frame["duration_sec"] = duration_sec
            frame["video_error"] = str(e)
            return frame

    def set_reference(self, url: str) -> Dict[str, Any]:
        self.reference_image_url = url
        return {
            "status": "ok",
            "reference": url,
            "message": "Master avatar reference updated.",
        }

    def status(self) -> Dict[str, Any]:
        return {
            "service": "saphira_avatar",
            "has_api_key": bool(self.api_key),
            "has_reference": bool(self.reference_image_url),
            "reference": self.reference_image_url or None,
            "cached_states": list(self._cache.keys()),
            "states": list(STATE_PROMPTS.keys()),
            "visual_dna": "Chelsea Megan Woods — platinum/black ombré, chest tattoo, black corset, neon blue + UV",
            "owner": "Chelsea Megan Woods",
        }


avatar_service = GrokAvatarService()
