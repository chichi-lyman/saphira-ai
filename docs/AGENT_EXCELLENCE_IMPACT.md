# Agent Excellence Impact Map

**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

Wiring excellence modules upgrades each internal agent’s execution, routing precision, and fallback reliability **without changing Saphira’s single unified voice** to the user.

| Internal agent | Excellence impact |
|---|---|
| **Saphira** (surface) | Capability-aware routing; offloads heavy work; keeps 180–350ms voice path for live interaction |
| **Aura** | `latency` + `edge_offline` for Piper TTS, ONNX wake-word, streaming STT duplex |
| **Agent Zero** | Full local authority via `edge_offline` + `latency` (Android/Termux/WebGPU/vLLM) |
| **Agent Two** | `tool_automation` — web tools / FastMCP with policy gating |
| **NovaReign** | `tool_automation` + `privacy_ledger` — a11y UI parse, screen actions, permissions |
| **NovaAethrea** | `memory_hybrid` — vector/context multi-session memory |
| **Scholar** | `reasoning` + `memory_hybrid` — multi-step analysis & synthesis |
| **Cipher** | `privacy_ledger` + `edge_offline` — audit logging, zero-egress checks |

## Dispatcher integration

`src/api/saphira_dispatcher.py`:

1. Sanitize utterance (`PrivacyFilter`)
2. `ExcellenceRouter.route()` / `route_excellence()`
3. `LatencyRouter.decide()`
4. Record turn in `dual_memory`
5. Resolve internal agent (event type + excellence pillars)
6. Dispatch + attach excellence metadata
7. Record telemetry sample

## Telemetry

- `GET /v1/saphira/excellence/stats` — live avg/p95 dispatch latency, path histogram, memory backend, pillar/agent hits
- `GET /v1/router/health` — local backend probes
- `POST /v1/router/execute` — one-shot excellence plan

## Rule

Never surface internal agent names in user-visible text. Metadata may list `internal_agent` for clients; spoken/written replies always say **Saphira**.
