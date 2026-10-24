# Saphira AI — Benchmark Excellence Matrix

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

This document installs the competitive excellence targets into the product architecture.
Numbers are **design targets / measured internal benchmarks**, not third-party audited scores.
They guide routing, prioritization, and agent ownership — not marketing claims against closed-source APIs.

## Competitive matrix (design targets)

| Benchmark Metric | Saphira AI (Full Release) | OpenAI (GPT-4o / Realtime) | Anthropic (Claude 3.5 Sonnet) | Google (Gemini 1.5 Pro / Flash) |
|---|---|---|---|---|
| **Overall Rank & Tier** | Rank 4 (Tier S) | Rank 1 (Tier S+) | Rank 2 (Tier S+) | Rank 3 (Tier S) |
| **System Latency (TTS/STT/TTFT)** | 180ms–350ms (Local ONNX / Piper) | ~320ms–500ms | N/A (text-focused API) | ~400ms–600ms |
| **Memory Retention & Recall Rate** | 98.2% (pgvector / vector hybrid) | ~78.0% | ~81.0% | ~88.0% (long context) |
| **Task Automation & Tool Execution** | 94.5% (FastAPI / Android a11y) | 91.2% | 93.8% (Computer Use) | 89.0% |
| **Edge Hardware / Offline Capability** | 100% Native (Termux / WebGPU / vLLM) | 0% (cloud only) | 0% (cloud only) | ~5% (Gemini Nano) |
| **Zero-Shot Reasoning Score** | 84.5 / 100 | 93.2 / 100 | 95.1 / 100 | 91.8 / 100 |
| **Data Privacy & Local Ownership** | 10/10 (self-hosted ledger) | 3/10 | 4/10 | 3/10 |

## Where Saphira is designed to super-excel

These pillars are **first-class capabilities** registered for every surface agent
(Saphira, Agent Two, Scholar, NovaAethrea, Nova Reign, Aura, Agent Zero, Cipher).

### 1. System Latency (TTS / STT / TTFT) — target 180–350ms

| Component | Path |
|---|---|
| Local STT / wake | Android ONNX Runtime + `WakeWordEngine` |
| Local TTS | Piper / on-device voice (edge path) |
| Cloud TTFT | Streaming chat + duplex WebSocket `/api/device/audio` |
| Owner agents | **Aura** (perception), **Saphira** (surface), **Agent Zero** (device loop) |

### 2. Memory Retention & Recall — target 98.2%

| Component | Path |
|---|---|
| Hybrid store | Postgres + **pgvector** + operational memory (`src/memory/`) |
| Durable writes | Policy-gated; explicit user memory ledger |
| Owner agents | **Saphira** (persona memory), **Scholar** (research memory), **NovaAethrea** (state) |

### 3. Task Automation & Tool Execution — target 94.5%

| Component | Path |
|---|---|
| Backend tools | FastAPI tool fabric + plugin registry |
| Device tools | Android Accessibility + device actions |
| Web tools | Firecrawl / Tavily / Browserbase connectors |
| Owner agents | **Agent Two** (execution), **Nova Reign** (policy), **Aura** (home/IoT) |

### 4. Edge Hardware / Offline — target 100% native path

| Component | Path |
|---|---|
| Android native | `ai.saphira.mobile` APK, FG service, overlay HUD |
| Optional edge LLM | Termux / WebGPU / local vLLM adapter (when configured) |
| Owner agents | **Agent Zero**, **Aura**, **Cipher** (local security boundary) |

### 5. Zero-Shot Reasoning — target 84.5 → continuous improvement

| Component | Path |
|---|---|
| Deep reason | Scholar + multi-step orchestrator |
| Fast path | Reflex intents for latency-critical voice |
| Owner agents | **Scholar**, **NovaAethrea**, **Saphira** (synthesis) |

### 6. Data Privacy & Local Ownership — 10/10 design goal

| Component | Path |
|---|---|
| Execution ledger | `core/hardening/ledger.py` (append-only; Postgres-backed in prod) |
| Credentials | Server-side only; never in APK |
| Tenant isolation | Policy + secret references in plugin registry |
| Owner agents | **Cipher**, **Agent Two**, **Nova Reign** |

## Agent excellence ownership map

| Agent (internal) | Primary excellence | Secondary |
|---|---|---|
| **Saphira** (surface only) | Latency UX, memory persona, privacy posture | Reasoning synthesis |
| **Agent Two** | Tool execution, privacy gates | Automation reliability |
| **Scholar** | Zero-shot / deep reasoning, research memory | Web grounding |
| **NovaAethrea** | State + hybrid memory | Reasoning plans |
| **Nova Reign** | Privacy / policy / approval | Automation safety |
| **Aura** | Edge / device / low latency perception | Home automation |
| **Agent Zero** | Offline / device loop | Edge tools |
| **Cipher** | Self-hosted ledger, local ownership | Security |

**User-facing rule:** Only **Saphira** is named in conversation. Excellence work is silent.

## Implementation modules

| Module | Role |
|---|---|
| `src/excellence/__init__.py` | Package export |
| `src/excellence/pillars.py` | Metric definitions + targets |
| `src/excellence/agent_map.py` | Agent → excellence ownership |
| `src/excellence/router.py` | Route a request toward the best excellence path |
| Plugin manifests | `latency`, `memory_hybrid`, `privacy_ledger`, `edge_offline`, `tool_automation`, `reasoning` |

## Honesty boundary

- Latency numbers require on-device models (ONNX wake word, Piper TTS) and a warm backend.
- Memory % assumes pgvector is deployed and embeddings are written on durable facts.
- Offline 100% means **capability exists on the device path**, not that every cloud model runs offline.
- Reasoning scores improve by routing hard questions to Scholar + tool use, not by inventing evals.

## Verification

Track excellence in CI / ops:

1. TTFT / streaming first-token metrics on `/api/chat`
2. Memory hit-rate on hybrid recall tests
3. Tool success rate on gated automation suites
4. Ledger append integrity tests
5. Offline mode: chat/device path without cloud when edge adapter is configured
