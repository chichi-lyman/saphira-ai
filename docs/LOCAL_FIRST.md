# Local-First vs Cloud — Honest Boundaries

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

Saphira is **not** a fully on-device general intelligence. She is a hybrid product that keeps the things that must be private or low-latency local, and routes heavy reasoning and high-quality voice through cloud providers under hard usage controls.

## What can run locally

- Wake-word / hot-word detection (when the client implements it)
- Lightweight on-device classifiers and intent hints
- Offline cache / SQLite-style recent context for short offline periods
- Local open-weight model endpoints (vLLM, Ollama) when the user or operator forces local mode or the cloud path is unavailable
- Face enrollment consent flow and local camera frame handling (actual recognition may still use a controlled backend)

## What uses cloud APIs

- Primary model responses (Gemini family by default, Claude as fallback, others via the registry)
- High-quality text-to-speech (ElevenLabs with Chelsea’s own voice clone, or configured alternatives)
- Real-time duplex voice sessions (LiveKit + model path)
- Heavy research, long-context synthesis, and multi-step agentic execution that exceeds local hardware budgets

## Cost & margin protection

Free-tier real-time voice is **hard-capped** (session + daily minutes). See `src/core/voice_usage_caps.py`. When a cap is hit the system continues in text and tells the user clearly. Uncapped free voice demos are intentionally disabled.

## Why this design

Trying to match the frontier labs on raw general-intelligence scale with a small team is a losing battle. Saphira’s edge is character, presence, the secret-masked multi-agent court, durable memory the user controls, and a clean understand → plan → execute → verify → remember loop. Local-first honesty keeps the product trustworthy and the unit economics survivable.

## Operator notes

- Set `SAPHIRA_VOICE_SESSION_CAP_MINUTES` and `SAPHIRA_VOICE_DAILY_CAP_MINUTES` in the environment.
- Force local inference with the router’s `force_local` flag or by omitting cloud keys.
- Never claim continuous always-on local general intelligence; that claim is false and erodes trust.
