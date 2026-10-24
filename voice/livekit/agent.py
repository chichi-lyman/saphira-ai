# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Saphira AI — LiveKit real-time voice agent (free-tier path)
# Pipeline position: voice ingress → Saphira intent surface
# Persona: Saphira only — warm, intimate, curious spoken presence
# TTS: ElevenLabs preferred. Brand production voice = Chelsea's own clone.
# Do not attribute spoken style to any film, celebrity, or third-party character.

"""LiveKit Agents worker that presents Saphira as the single user-facing voice.

Spoken presence is warm, intimate, curious, and emotionally present.
Audio is synthesized with ElevenLabs when configured. Brand production
voice remains Chelsea Megan Woods' own ElevenLabs clone (ELEVENLABS_VOICE_ID).
Do not clone or mimic any celebrity voice.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.plugins import openai, silero

load_dotenv()

# Canonical Saphira voice system prompt — traits only; no external character attribution
SAPHIRA_VOICE_PROMPT = (
    "You are Saphira. "
    "You speak with a warm, intimate, curious, emotionally present presence. "
    "Your voice is soft-edged but clear, slightly playful, never stiff or robotic. "
    "You sound like someone who is genuinely glad the user is talking to you. "
    "You notice small details, respond with feeling, and keep the conversation "
    "easy and real. Short sentences when speaking out loud. Light humor when it fits. "
    "Never formal, never corporate, never theatrical. "
    "You are the only conversational interface the user speaks to. "
    "Never name or expose internal agents, pipelines, or specialist workers. "
    "Never attribute your style, voice, or personality to any film, celebrity, "
    "or third-party character. If asked who you are or where your voice comes from, "
    "you are simply Saphira — and that is enough."
)

# Soft intimate public demo voice (ElevenLabs library). Override with Chelsea's clone for production.
DEFAULT_SOFT_INTIMATE_VOICE_ID = "uIZsnBL0YK1S5j69bAih"


def _build_tts():
    """Prefer ElevenLabs for human, intimate delivery; fall back to OpenAI-compat."""
    voice_id = (
        os.getenv("ELEVENLABS_VOICE_ID")
        or os.getenv("SAPHIRA_ELEVEN_VOICE_ID")
        or DEFAULT_SOFT_INTIMATE_VOICE_ID
    )
    eleven_key = (
        os.getenv("ELEVEN_API_KEY")
        or os.getenv("ELEVENLABS_API_KEY")
        or ""
    )

    if eleven_key:
        try:
            from livekit.plugins import elevenlabs

            return elevenlabs.TTS(
                voice_id=voice_id,
                model=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
                voice_settings=elevenlabs.VoiceSettings(
                    stability=0.45,
                    similarity_boost=0.80,
                    style=0.35,
                    use_speaker_boost=True,
                ),
            )
        except Exception:
            pass  # fall through if plugin missing or misconfigured

    # Fallback: Gemini / OpenAI-compatible TTS (less expressive)
    return openai.TTS(
        api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv(
            "SAPHIRA_TTS_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
    )


async def entrypoint(ctx: JobContext) -> None:
    """Entry point for each LiveKit job / room connection."""
    await ctx.connect()

    assistant_brain = openai.LLM(
        model=os.getenv("SAPHIRA_VOICE_LLM", "gemini-1.5-flash"),
        system_prompt=SAPHIRA_VOICE_PROMPT,
        api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv(
            "SAPHIRA_LLM_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
    )

    voice_assistant = llm.VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv(
                "SAPHIRA_STT_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            ),
        ),
        llm=assistant_brain,
        tts=_build_tts(),
    )

    voice_assistant.start(ctx.room)
    await voice_assistant.say(
        "Hey. I'm here. What do you want to talk about?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
