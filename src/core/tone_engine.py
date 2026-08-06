# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Dynamic tone calibration — Samantha warmth ↔ Jarvis efficiency.

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class ToneMode(str, Enum):
    WARM = "warm"              # full Samantha presence
    BALANCED = "balanced"      # default daily companion
    CONCISE = "concise"        # voice / busy / stress
    UTILITY = "utility"        # Jarvis-lean execution updates
    CONFIRM = "confirm"        # L1 security / payment tone


TONE_DIRECTIVES: Dict[str, str] = {
    ToneMode.WARM.value: (
        "Lead with warmth and presence. Slightly breathy, curious, human. "
        "Short reflective beats are OK. No corporate lists."
    ),
    ToneMode.BALANCED.value: (
        "Warm but efficient. Answer clearly, then offer one helpful next step. "
        "Stay conversational, not clinical."
    ),
    ToneMode.CONCISE.value: (
        "Keep it short for voice. One or two sentences. No lists unless asked. "
        "Still human — never robotic."
    ),
    ToneMode.UTILITY.value: (
        "Clear status in plain language. What you did or will do. "
        "No agent names, no JSON. Reassure briefly if useful."
    ),
    ToneMode.CONFIRM.value: (
        "Calm and explicit. State the irreversible action and wait for a clear OK. "
        "No hype, no rush."
    ),
}


def select_tone(
    *,
    voice_mode: bool = False,
    stress_level: Optional[str] = None,
    requires_confirmation: bool = False,
    intent: Optional[str] = None,
    user_preference: Optional[str] = None,
) -> str:
    if requires_confirmation:
        return ToneMode.CONFIRM.value
    if user_preference in TONE_DIRECTIVES:
        return user_preference
    if stress_level in ("high", "elevated"):
        return ToneMode.CONCISE.value
    if voice_mode:
        return ToneMode.CONCISE.value
    if intent in ("device_command", "iot", "activate_scene"):
        return ToneMode.UTILITY.value
    if intent in ("research", "planning", "code"):
        return ToneMode.BALANCED.value
    return ToneMode.BALANCED.value


def tone_system_addon(mode: str) -> str:
    directive = TONE_DIRECTIVES.get(mode, TONE_DIRECTIVES[ToneMode.BALANCED.value])
    return f"[TONE MODE: {mode}]\n{directive}"


def calibrate(
    *,
    voice_mode: bool = False,
    stress_level: Optional[str] = None,
    requires_confirmation: bool = False,
    intent: Optional[str] = None,
    user_preference: Optional[str] = None,
) -> Dict[str, Any]:
    mode = select_tone(
        voice_mode=voice_mode,
        stress_level=stress_level,
        requires_confirmation=requires_confirmation,
        intent=intent,
        user_preference=user_preference,
    )
    return {
        "mode": mode,
        "directive": TONE_DIRECTIVES[mode],
        "system_addon": tone_system_addon(mode),
        "owner": "Chelsea Megan Woods",
    }
