# Saphira + Google Vertex AI (Brain)

© 2026 Chelsea Megan Woods · Nova Umbrella / Woods AI Studio

This monorepo treats **Vertex AI** as the preferred production brain for Gemini models, with automatic fallback to the Gemini Developer API (AI Studio key).

## Dual-mode Gemini provider

| Mode | When | Auth | Env |
|------|------|------|-----|
| **Vertex AI** (preferred) | `GOOGLE_CLOUD_PROJECT` is set and `VERTEX_ENABLED=true` | Application Default Credentials (ADC) or service account | `GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION` |
| **Developer API** | No project (or Vertex disabled) | API key | `GEMINI_API_KEY` |

The same `google-genai` SDK is used for both:

```python
from google import genai

# Vertex
client = genai.Client(vertexai=True, project="your-project", location="us-central1")

# Developer
client = genai.Client(api_key="...")
```

## Quick setup (Vertex)

1. Create or select a GCP project and enable the Vertex AI API.
2. Authenticate for local/dev:

   ```bash
   gcloud auth application-default login
   # or
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
   ```

3. Copy `.env.example` → `.env` and set:

   ```bash
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   VERTEX_LOCATION=us-central1
   VERTEX_ENABLED=true
   GEMINI_MODEL=gemini-2.5-flash
   SAPHIRA_PROVIDERS_ENABLED=true
   SAPHIRA_LLM_PREFERENCE=gemini,anthropic,openai,xai
   ```

4. Optional: keep `GEMINI_API_KEY` as a cold-start fallback when Vertex is unavailable.

5. Confirm health:

   ```bash
   # After starting the API
   curl -s localhost:8000/api/health | jq '.providers.gemini'
   ```

   Expect `"backend": "vertex"` when project is configured.

## Models

Default model: `gemini-2.5-flash` (high context, interactive).

Registry keys (see `src/core/model_registry.py`):

- `vertex_gemini_flash` / `vertex_gemini_pro` — Vertex path
- `gemini_flash` / `gemini_pro` — Developer API path

## Production notes

- Prefer a dedicated service account with `roles/aiplatform.user` (or tighter custom role).
- Pin region for latency and data residency (`VERTEX_LOCATION`).
- Master switch `SAPHIRA_PROVIDERS_ENABLED=false` blocks all external LLM calls (safe default in template).
- Circuit breakers and preference order in `ProviderRegistry` still apply; Gemini is first in the default preference list.

## Related files

- `src/providers/adapters.py` — `GeminiAdapter` dual-mode client
- `src/config/settings.py` — `google_cloud_project`, `vertex_location`, `vertex_enabled`
- `src/connectors/gemini.py` — lightweight connector (same dual-mode logic)
- `src/core/model_registry.py` — endpoint registry including Vertex entries
- `.env.example` — variable template
