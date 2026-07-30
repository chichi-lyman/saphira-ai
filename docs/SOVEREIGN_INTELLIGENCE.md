# Sovereign Intelligence Systems – Deployment Guide
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

Sovereign Intelligence means the entire Saphira stack (models, memory, agents, biometrics, IoT) can run under the user’s sole control with zero mandatory dependence on public third-party clouds for inference or storage of sensitive data.

## Goals
- Keep financial, health, relationship, and home data private by default.
- Allow optional hybrid use of cloud models when the user explicitly opts in.
- Support fully offline / air-gapped operation for high-security environments.

## Recommended Self-Hosted Stack

| Layer | Recommended Options | Notes |
|-------|---------------------|-------|
| LLM Inference | Ollama, llama.cpp, vLLM, LocalAI, LM Studio | Prefer quantized GGUF / AWQ models that fit the target hardware |
| Embedding / RAG | sentence-transformers + Chroma / LanceDB / SQLite-VSS | Fully local vector store |
| Orchestration | Existing Saphira Python agents + FastAPI | Already designed for local execution |
| Wearables | Flutter platform channel → Health Connect / HealthKit | Data never leaves the device unless user enables cloud sync |
| IoT | Home Assistant + Matter (local network) | Already integrated via `matter_home_assistant` |
| Voice | Piper / Coqui TTS + Whisper.cpp or Vosk | Offline STT/TTS |
| Container | Docker Compose (see `deploy/docker-compose.prod.yml`) | Single-node or small cluster |

## Deployment Patterns

### 1. Single-User Desktop / Laptop
```bash
# Start local LLM
ollama serve
ollama pull llama3.2:3b   # or larger if hardware allows

# Configure Saphira to point at local endpoint
export SAPHIRA_LLM_BASE_URL=http://localhost:11434/v1
export SAPHIRA_LLM_MODEL=llama3.2:3b

uvicorn main:app --host 127.0.0.1 --port 8000
```

### 2. Home Server / NUC (always-on)
- Run the Docker Compose stack from `deploy/`.
- Bind the API only to the LAN or use a reverse proxy with mutual TLS.
- Store persistent memory and biometric history on encrypted volumes.

### 3. Fully Air-Gapped
- Pre-load model weights and container images on offline media.
- Disable all outbound network in the compose file.
- Use only the mock or locally bridged wearable path.
- Intent classification and stress estimation already run without network.

## Security Controls Already Present
- Dual-prompt security layer (`src/core/dual_prompt_security.py`)
- Autonomy gates and confirmation for sensitive actions (Agent Two)
- Governance allow-list (Nova Reign)
- Self-healing with bounded retries
- No vendor model names or system prompts leaked to client-side code

## Hybrid Mode (Optional)
Users who want occasional cloud capability can set:
```bash
SAPHIRA_ALLOW_CLOUD_FALLBACK=true
SAPHIRA_CLOUD_PROVIDER=openai|anthropic|xai   # only when explicitly enabled
```
All cloud calls should be logged and require a one-time user confirmation for the session.

## Next Implementation Steps
1. Add an OpenAI-compatible local client wrapper that prefers Ollama / vLLM.
2. Persist biometric history and stress scores in the existing NovaAethrea store under an encrypted key.
3. Expose a simple “Sovereign Mode” toggle in the Flutter / web UI that disables every external endpoint.
4. Document hardware sizing (CPU/GPU RAM) for common model families.

*Saphira is designed so that the default, most private path is also the most complete path.*
