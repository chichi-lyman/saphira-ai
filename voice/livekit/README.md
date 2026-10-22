# Saphira LiveKit Voice Agent

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

Free-tier real-time voice path for **Saphira** using [LiveKit Agents](https://github.com/livekit/agents) + Google Gemini.

Saphira remains the only user-facing identity. Internal pipeline agents are never named.

## What this gives you

- Real-time duplex voice (STT → LLM → TTS) with barge-in / interruption support
- LiveKit Cloud free tier: ~1,000 minutes/month of WebRTC streaming
- Gemini 1.5 Flash free-tier brain (via OpenAI-compatible endpoint)
- Silero VAD for turn detection
- Drop-in worker that connects to LiveKit Cloud Sandbox or your own frontend

## Prerequisites (all free)

1. **Python 3.10+**
2. **Google AI Studio** → free Gemini API key  
   https://aistudio.google.com/
3. **LiveKit Cloud** → free project (URL, API Key, API Secret)  
   https://cloud.livekit.io/

## Setup

```bash
cd voice/livekit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
```

### `.env`

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
GEMINI_API_KEY=...
# Optional overrides
# SAPHIRA_VOICE_LLM=gemini-1.5-flash
# SAPHIRA_LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## Run

```bash
python agent.py dev
```

Then open the LiveKit Cloud **Sandbox / Agents** tab, connect, unmute mic. Saphira answers in real time.

Production-style start:

```bash
python agent.py start
```

## Alignment with Saphira monorepo

| Concern | Location |
|---------|----------|
| Persona / identity | `identity/IDENTITY.md` + system prompt in `agent.py` |
| TTS voice clone (ElevenLabs) | `src/core/saphira_voice.py` (preferred for production branding) |
| Existing STT / wake / barge-in | `voice/stt_stream.py`, `voice/wake_word.py`, `voice/interruption_orchestrator.py` |
| Executive pipeline | Saphira (intent) → … → Agent Zero (execution) — this worker is **ingress only** |

For production, route LiveKit transcripts into the main FastAPI / orchestrator so memory, governance, and tools stay on the canonical path. This standalone worker is ideal for rapid voice prototyping and demos.

## Next steps

- Add `@function_tool` handlers that call Saphira capability registry / connectors
- Swap Gemini TTS for ElevenLabs clone of Chelsea’s voice (`saphira_voice.py`)
- Pair with LiveKit React / Flutter frontend or Android templates
- Optional privacy path: replace Gemini with local Ollama + local STT/TTS

## References

- LiveKit Agents docs: https://docs.livekit.io/agents/
- LiveKit Python examples: https://github.com/livekit-examples/python-agents-examples
- Original free JARVIS-style walkthrough pattern adapted here for Saphira identity
