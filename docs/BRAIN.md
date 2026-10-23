# SaphiraBrain — Connecting Saphira to Her Models

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

Saphira is connected to a multi-provider **brain** through a single explicit entry point:

```text
src/core/saphira_brain.py  →  SaphiraBrain
```

## What the brain does

1. **Locks persona** — Every call injects the Samantha-style system prompt (warm, intimate, non-generic).
2. **Locks competitive positioning** — Injects the directive that Saphira wins on character and the full execution loop, not on out-scaling Google/OpenAI/Anthropic.
3. **Routes across providers** with ordered fallback:
   - Gemini (primary, fast)
   - Anthropic / Claude (strong coding + long context)
   - OpenAI
   - xAI / Grok
4. **Falls back cleanly** when a key is missing or a provider errors.

## Surfaces that use the brain

| Surface | Path | Notes |
|---------|------|--------|
| HTTP chat | `POST /chat` | Full conversational + orchestrator result |
| WebSocket live | `WS /v1/saphira/stream` | Default Saphira path + scholar reasoning |

Internal structural agents (aura, novareign, cipher, agent_zero, agent_two) stay non-LLM. Only user-facing natural language goes through the brain.

## Enable the brain

In `.env` / deployment secrets:

```bash
SAPHIRA_PROVIDERS_ENABLED=true

# At least one of:
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
XAI_API_KEY=...

# Optional tuning
SAPHIRA_LLM_PREFERENCE=gemini,anthropic,openai,xai
GEMINI_MODEL=gemini-2.0-flash
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
OPENAI_MODEL=gpt-4o-mini
XAI_MODEL=grok-2-latest
```

## Usage in code

```python
from src.core.saphira_brain import get_saphira_brain

brain = get_saphira_brain()

# Full control
result = await brain.think("Help me plan the next sprint")

# Convenience for chat / live
text = await brain.reply("What should I focus on today?")
```

## Design rule

Saphira does **not** try to be a bigger general-intelligence brain than the frontier labs.
She uses strong models as interchangeable engines behind a distinct character, a secret-masked multi-agent court, durable memory, and a policy-gated execution loop.

That is the correct connection.
