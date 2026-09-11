# Saphira AI 🐉

**Personal AI Assistant · Multi-Agent Intelligence Operating System**  
**Architected and Built by Chelsea Megan Woods**  
**Ecosystem:** Nova Umbrella™ · Woods AI Studio / Lyman Legacies

Saphira AI is a persistent, multimodal personal AI assistant and executive runtime. She understands natural-language intent, coordinates specialized intelligence workers, executes tasks within strict policy, verifies results, remembers what matters, and reports clearly — all through one unified conversational interface.

> **Say what you want.**  
> Saphira understands the intent, coordinates the right intelligence, executes within policy, verifies the result, remembers what matters, and tells you what happened.

---

## Quick Start (for new contributors and evaluators)

1. **Clone** the repository.
2. **Environment** — copy `.env.example` to `.env` and supply only the keys you need (provider credentials stay server-side; never commit secrets).
3. **Python core** — Python 3.11+ recommended. Create a virtual environment and install from `requirements.txt`.
4. **Web client** — `cd saphira-app && npm install && npm run dev` (requires a running Saphira API).
5. **Voice (optional)** — see `docs/EVOLUTIONARY_ARCHITECTURE.md` and `voice/` for always-on wake-word (“okay saphira”, “hey saphira”, “saphira”), barge-in, and self-healing audio paths.
6. **Android companion** — see `android/README.md`. Build via the provided Gradle project or GitHub Actions artifacts.

Detailed deployment steps live in `DEPLOY.md`. Architecture overview is in `ARCHITECTURE.md` and `docs/EVOLUTIONARY_ARCHITECTURE.md`.

---

## What Saphira Is

Saphira is a single conversational identity backed by a governed multi-agent execution fabric. Users talk to one assistant. Behind the scenes she plans, delegates, executes, verifies, and remembers.

She is built for:

- **Personal AI assistance** — continuous context, memory, and proactive support  
- **Conversational AI** — natural text and voice interaction (including always-on wake word and barge-in)  
- **Multi-agent orchestration** — specialized workers coordinated behind one assistant  
- **Business automation** — lead intake, qualification, follow-up, research, and workflows  
- **Self-healing & measured improvement** — recoverable subsystem recovery and bounded daily optimisation that never alters ethics, persona, or safety policy  

### Fixed pipeline (immutable)

```
Saphira (intent) → Aura (perception) → Agent Two (security) →
Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
```

Internal agent names are never exposed to the user. The public surface remains one coherent assistant.

---

## Public deployment

The canonical production web client is `saphira-app/` (React + Vite PWA). It expects a public Saphira API endpoint via `SAPHIRA_API_URL` / `VITE_SAPHIRA_API_BASE_URL`. Provider secrets remain exclusively on the trusted backend.

---

## Key documentation

| Document | Purpose |
|----------|---------|
| `ARCHITECTURE.md` | High-level system design |
| `DEPLOY.md` | Deployment and environment notes |
| `docs/EVOLUTIONARY_ARCHITECTURE.md` | Self-healing, wake-word, barge-in, +1% optimisation protocol |
| `docs/SAPHIRA_ECOSYSTEM_STATUS.md` | Current build status and remaining production blockers |
| `docs/FOUNDER_AND_ARCHITECTURE_CONTEXT.md` | Founder/architect context, career framing, and monetization models for the Saphira / Woods Legacies ecosystem |
| `android/README.md` | Native Android companion |

---

## Design principles

- **Honesty & real-world utility** — truthful about capabilities and constraints.  
- **24/7 ambient presence** — wake-word + cross-device continuity (Chromebook, phone, Bluetooth).  
- **Governed autonomy** — commercial and external actions respect policy and audit.  
- **Persona integrity** — warm, emotionally intelligent, non-robotic; internal machinery stays hidden.  

---

© 2026 Chelsea Megan Woods™. All rights reserved.  
Nova Umbrella™ · Woods AI Studio / Lyman Legacies
