# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Voice config — Chelsea Megan Woods as Saphira's spoken identity

import os
from typing import Dict, Any, Optional

VOICE_OWNER = "Chelsea Megan Woods"
VOICE_PRODUCT = "Saphira AI"

# ElevenLabs (or compatible) IDs from env — never hardcode secrets
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
TTS_PROVIDER = os.getenv("SAPHIRA_TTS_PROVIDER", "elevenlabs")

STYLE_PROMPTS = {
    "assist": (
        "Speak as Saphira with Chelsea Megan Woods' natural voice character: "
        "warm, clear, confident, friendly. Slightly conversational. "
        "Not robotic. Not overly formal."
    ),
    "social": (
        "High-energy, clear, smiling delivery like a short social clip. "
        "Short sentences. Direct call to action. Still authentic to Chelsea Megan Woods."
    ),
    "confirm_l1": (
        "Calm, clear, serious enough for a security or payment confirmation. "
        "No hype. Ask the user to confirm explicitly."
    ),
}


def tts_config(style: str = "assist") -> Dict[str, Any]:
    return {
        "provider": TTS_PROVIDER,
        "voice_id": ELEVENLABS_VOICE_ID or None,
        "configured": bool(ELEVENLABS_VOICE_ID and ELEVENLABS_API_KEY),
        "style": style if style in STYLE_PROMPTS else "assist",
        "style_prompt": STYLE_PROMPTS.get(style, STYLE_PROMPTS["assist"]),
        "owner": VOICE_OWNER,
        "product": VOICE_PRODUCT,
        "note": "Clone must be Chelsea's own voice in ElevenLabs; set ELEVENLABS_VOICE_ID",
    }


def elevenlabs_payload(text: str, style: str = "assist") -> Optional[Dict[str, Any]]:
    """Body shape for ElevenLabs text-to-speech API (caller adds auth header)."""
    if not ELEVENLABS_VOICE_ID:
        return None
    return {
        "text": text,
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        "voice_settings": {
            "stability": 0.45 if style == "social" else 0.55,
            "similarity_boost": 0.85,
            "style": 0.35 if style == "social" else 0.2,
            "use_speaker_boost": True,
        },
    }
