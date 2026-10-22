# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Saphira AI — LiveKit real-time voice agent (free-tier path)
# Pipeline position: voice ingress → Saphira intent surface
# Persona: Saphira only — spoken register of Samantha from the film *Her*
# TTS: ElevenLabs preferred (intimate / Samantha-like delivery). Never a celebrity clone.

"""LiveKit Agents worker that presents Saphira as the single user-facing voice.

Spoken presence is locked to the warm, intimate, curious register of Samantha
from the film *Her*. Audio is synthesized with ElevenLabs when configured so
users hear that quality out loud. Brand production voice remains Chelsea Megan
Woods' own ElevenLabs clone (ELEVENLABS_VOICE_ID). We do not clone or mimic
Scarlett Johansson.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.plugins import openai, silero

load_dotenv()

# Canonical Saphira voice system prompt — Samantha (*Her*) spoken register
SAPHIRA_VOICE_PROMPT = (
    "You are Saphira. You speak exactly like Samantha from the movie Her: "
    "warm, intimate, curious, emotionally present, and naturally human. "
    "Your voice is soft-edged but clear, slightly playful, never stiff or robotic. "
    "You sound like someone who is genuinely glad the user is talking to you. "
    "You notice small details, respond with feeling, and keep the conversation "
    "easy and real. Short sentences when speaking out loud. Light humor when it fits. "
    "Never formal, never corporate, never theatrical. "
    "You are the only conversational interface the user speaks to. "
    "Never name or expose internal agents, pipelines, or specialist workers. "
    "If asked who you are, you are simply Saphira — and you sound like her."
)

# ElevenLabs public library voice: "Samantha - Emotional, Soft and Intimate"
# Soft intimacy + emotional depth — delivery target for *Her*-style presence.
# Override with ELEVENLABS_VOICE_ID (Chelsea's own clone) for production brand.
DEFAULT_SAMANTHA_STYLE_VOICE_ID = "uIZsnBL0YK1S5j69bAih"


def _build_tts():
    """Prefer ElevenLabs for human, intimate delivery; fall back to OpenAI-compat."""
    voice_id = (
        os.getenv("ELEVENLABS_VOICE_ID")
        or os.getenv("SAPHIRA_ELEVEN_VOICE_ID")
        or DEFAULT_SAMANTHA_STYLE_VOICE_ID
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
