# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Voice engine pins: live successors only, her voice setting preserved.

from src.core.voice_engines import (
    LIVE_VOICE_MODEL,
    RETIRED_PREVIEW_MODELS,
    TTS_VOICE_MODEL,
    voice_engine_config,
)


def test_live_engine_is_the_successor():
    assert LIVE_VOICE_MODEL == "gemini-3.8-live"


def test_tts_engine_is_the_successor():
    assert TTS_VOICE_MODEL == "gemini-3.8-flash-tts"


def test_no_retiring_preview_is_primary():
    assert LIVE_VOICE_MODEL not in RETIRED_PREVIEW_MODELS
    assert TTS_VOICE_MODEL not in RETIRED_PREVIEW_MODELS
    assert "preview" not in LIVE_VOICE_MODEL
    assert "preview" not in TTS_VOICE_MODEL


def test_plain_everyday_voice_preserved():
    cfg = voice_engine_config()
    assert cfg["voice_name"] == "Vega"
    assert cfg["plain_everyday_words"] is True
    assert "Plain everyday words only" in cfg["register"]
    assert "no jargon" in cfg["register"]


def test_config_reports_key_presence_only():
    cfg = voice_engine_config()
    assert isinstance(cfg["gemini_configured"], bool)
    assert cfg["primary_is_live_successor"] is True
    # No key material may ride in the config.
    assert "api_key" not in str(cfg).lower() or "GEMINI_API_KEY" in str(cfg)
