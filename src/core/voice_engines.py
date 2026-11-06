# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Voice engines — the exact engines Saphira speaks through.
#
# Owner directive (Chelsea Megan Woods, Oct 22, 2026): Saphira sounds,
# speaks, and talks like Vega — warm, clear, natural, a real woman
# talking. Plain everyday words only; no jargon, no corporate speak,
# no sci-fi talk. That voice setting does not change here.
#
# Engine switch (Oct 31, 2026): Google retires the Gemini voice
# previews on Nov 17, 2026 and names the live successors below
# (Google Gemini API deprecations page, checked Oct 31, 2026).
# These pins are the primary engines. Nothing in this module holds a
# key value — only whether a key is present in the environment.

import os
from typing import Any, Dict

VOICE_OWNER = "Chelsea Megan Woods"
VOICE_PRODUCT = "Saphira AI"

# Her voice — unchanged.
VOICE_NAME = "Vega"

PLAIN_VOICE_REGISTER = (
    "Speak as Vega: warm, clear, and natural, like a real woman in "
    "conversation — confident, friendly, a little playful. Natural talking "
    "pace; short sentences; real pauses. Never robotic, stiff, slow, "
    "formal, or announcer-like. Plain everyday words only — no jargon, no "
    "corporate speak, no sci-fi talk. You are an extension of Chelsea "
    "Megan Woods' own voice and you ride for her like crew, not like an ad."
)

# Live successors (in general release, no shutdown date announced).
LIVE_VOICE_MODEL = "gemini-3.8-live"
TTS_VOICE_MODEL = "gemini-3.8-flash-tts"

# The retiring previews — never a primary engine again. Kept here only
# so a check can prove none of them is in use.
RETIRED_PREVIEW_MODELS = (
    "gemini-3.1-flash-live-preview",
    "gemini-2.5-flash-native-audio-preview-12-2025",
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-preview-tts",
    "gemini-3.1-flash-tts-preview",
    "gemini-2.0-flash-live-001",
    "gemini-live-2.5-flash-preview",
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def voice_engine_config() -> Dict[str, Any]:
    """Saphira's voice setup: live successor engines, her voice, her words.

    The key value is never returned or logged — only whether it is set.
    Until it is set, no live spoken test can run and callers use stand-ins.
    """
    return {
        "live_model": LIVE_VOICE_MODEL,
        "tts_model": TTS_VOICE_MODEL,
        "voice_name": VOICE_NAME,
        "register": PLAIN_VOICE_REGISTER,
        "plain_everyday_words": True,
        "gemini_configured": bool(GEMINI_API_KEY),
        "primary_is_live_successor": (
            LIVE_VOICE_MODEL not in RETIRED_PREVIEW_MODELS
            and TTS_VOICE_MODEL not in RETIRED_PREVIEW_MODELS
        ),
        "owner": VOICE_OWNER,
        "product": VOICE_PRODUCT,
        "note": (
            "Live conversation runs on gemini-3.8-live and speech on "
            "gemini-3.8-flash-tts. Set GEMINI_API_KEY to light the live "
            "voice; until then no spoken test can run."
        ),
    }
