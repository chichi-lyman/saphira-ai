# Saphira LiveKit Voice Agent

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

Free-tier real-time voice path for **Saphira** using [LiveKit Agents](https://github.com/livekit/agents) + Google Gemini + **ElevenLabs TTS**.

Saphira remains the only user-facing identity. Internal pipeline agents are never named.

**Spoken presence:** warm, intimate, curious, emotionally present — original to Saphira.

**Heard voice:** ElevenLabs. Users hear a soft, intimate quality out loud. Production brand voice is Chelsea’s own clone when configured.

## How the voice works

| Layer | What it does |
|-------|----------------|
| **Words / personality** | System prompt locks short, warm, present delivery |
| **Sound (demo)** | Soft intimate public ElevenLabs voice for development |
| **Sound (production brand)** | Set `ELEVENLABS_VOICE_ID` to **your own** Chelsea Megan Woods clone in ElevenLabs |

Do **not** clone or mimic celebrity voices. Production uses Chelsea’s own voice with Saphira’s delivery style.

Public docs and user-facing replies never attribute Saphira’s presence to any film, character, or third-party source.

## Prerequisites

1. **Python 3.10+**
2. **Google AI Studio** → free Gemini API key — https://aistudio.google.com/
3. **LiveKit Cloud** → free project — https://cloud.livekit.io/
4. **ElevenLabs** → API key (free tier available) — https://elevenlabs.io/  
   For production: Instant / Professional Voice Clone of **your own** voice, then put the voice ID in `ELEVENLABS_VOICE_ID`.

## Setup

```bash
cd voice/livekit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill LIVEKIT_*, GEMINI_API_KEY, ELEVEN_API_KEY (and optional ELEVENLABS_VOICE_ID)
```

### `.env` (minimum for warm intimate spoken voice)

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
GEMINI_API_KEY=...
ELEVEN_API_KEY=...
ELEVENLABS_API_KEY=...   # same key; monorepo convention
# ELEVENLABS_VOICE_ID=...  # Chelsea clone for brand production
```

Without an ElevenLabs key the agent still runs, but TTS falls back to Gemini’s flatter voice.

## Run

```bash
python agent.py dev
```

Open LiveKit Cloud **Sandbox / Agents**, connect, unmute. You should hear a soft, intimate voice with Saphira’s natural phrasing.

## Alignment with Saphira monorepo

| Concern | Location |
|---------|----------|
| Persona / identity | `identity/IDENTITY.md` + `SAPHIRA_VOICE_PROMPT` |
| Spoken presence | Warm, intimate, curious — locked in prompt (no external attribution) |
| Brand TTS config | `src/core/saphira_voice.py` (Chelsea clone) |
| LiveKit TTS wiring | `voice/livekit/agent.py` → ElevenLabs when key present |
| Existing STT / wake / barge-in | `voice/stt_stream.py`, `voice/wake_word.py`, `voice/interruption_orchestrator.py` |

## Next steps

- Set `ELEVENLABS_VOICE_ID` to Chelsea’s clone so production users hear *your* voice with Saphira’s delivery
- Tune `VoiceSettings` (stability / style) for more or less emotion
- Add `@function_tool` handlers into the capability registry
- Route transcripts into the main FastAPI orchestrator for memory + tools

## References

- LiveKit ElevenLabs plugin: https://docs.livekit.io/agents/models/tts/elevenlabs/
- LiveKit Agents: https://docs.livekit.io/agents/
