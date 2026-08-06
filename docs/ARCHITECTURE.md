# Saphira AI Architecture

*Architect: Chelsea Megan Woods · Woods Legacies*

This document maps how wake-word, persona, routing, tools, and background execution connect.

---

## High-level flow

```
┌─────────────────────────────────────────────────────────────┐
│  Edge: OpenWakeWord / Widget / Node mic                     │
│  (local, low CPU; custom saphira.onnx optional)             │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /presence/wake
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Presence layer                                             │
│  · Wake session + greeting (conversational upfront)         │
│  · Widget state (listening / talking / background_busy)     │
│  · Avatar frame hints                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /presence/utter or /chat
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Core intelligence                                          │
│  · Persona engine (Samantha warmth + secret mask)           │
│  · Tone engine (warm / concise / utility / confirm)         │
│  · Session memory + persistent memory                       │
│  · Model router (local → fast → heavy)                      │
│  · Multi-agent orchestrator (intent → security → execute)   │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
     ┌──────────────────┐          ┌──────────────────────────┐
     │  Foreground      │          │  Background worker (L3)  │
     │  Public reply    │          │  IoT, research, memory   │
     │  TTS / widget    │          │  Quiet completion        │
     └──────────────────┘          └──────────────────────────┘
```

---

## Layers

### 1. Core intelligence & persona
| Module | Role |
|--------|------|
| `src/core/saphira_persona.py` | Locked public persona |
| `src/core/tone_engine.py` | Dynamic tone calibration |
| `src/core/memory_layers.py` | Session + long-term memory |
| `src/core/model_router.py` | Multi-model fallback |
| `src/core/orchestrator.py` | Agent pipeline |

### 2. Interface & I/O
| Surface | Role |
|---------|------|
| `/presence/*` | Wake, utter, widget, background |
| `/chat` | Text chat |
| `/avatar` | Visual presence |
| `/nodes` | Companion device registry |
| Multimodal registry | Image / audio / screen hooks |

### 3. Action & execution
| Module | Role |
|--------|------|
| `src/core/tool_registry.py` | Function calling + L1/L2/L3 gates |
| `src/core/background_worker.py` | Non-blocking real-world jobs |
| `src/core/autonomy_levels.py` | Confirm / supervised / silent |
| IoT controllers in `main.py` | Physical control matrix |

### 4. Deployment & DX
| Asset | Role |
|-------|------|
| `setup.sh` | One-step install |
| `.env.example` | Keys and feature flags |
| `docs/ARCHITECTURE.md` | This file |
| `models/wakeword/` | Custom OpenWakeWord models |
| `ROADMAP.md` | Status tracking |

---

## Autonomy guardrails

| Level | Behavior | Examples |
|-------|----------|----------|
| **L1** | Confirm first | Unlock, payment, shell, send email |
| **L2** | Supervised / bounded | Lights, vacuum, calendar list |
| **L3** | Silent background | Memory write, telemetry, research ingest |

---

## Design principle

> **Talk first when woken. Act quietly in the background.**  
> Never expose agent codenames or raw JSON to the user.

---

*Last updated: 2026-08-06*
