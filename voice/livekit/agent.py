# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Saphira AI — LiveKit real-time voice agent (free-tier path)
# Pipeline position: voice ingress → Saphira intent surface
# Persona: Saphira only — spoken register of Samantha from the film *Her*

"""LiveKit Agents worker that presents Saphira as the single user-facing voice.

Uses LiveKit Cloud free tier + Google Gemini (via OpenAI-compatible plugin)
for a low-cost, low-latency voice pipeline. Spoken presence is locked to the
warm, intimate, curious register of Samantha from the film *Her*.
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


async def entrypoint(ctx: JobContext) -> None:
    """Entry point for each LiveKit job / room connection."""
    await ctx.connect()

    # Brain: Gemini 1.5 Flash via OpenAI-compatible endpoint (generous free tier)
    assistant_brain = openai.LLM(
        model=os.getenv("SAPHIRA_VOICE_LLM", "gemini-1.5-flash"),
        system_prompt=SAPHIRA_VOICE_PROMPT,
        api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv(
            "SAPHIRA_LLM_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
    )

    # Real-time voice pipeline: VAD → STT → LLM → TTS
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
        tts=openai.TTS(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv(
                "SAPHIRA_TTS_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            ),
        ),
    )

    voice_assistant.start(ctx.room)
    await voice_assistant.say(
        "Hey. I'm here. What do you want to talk about?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
