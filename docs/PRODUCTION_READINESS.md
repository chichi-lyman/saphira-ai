# Saphira AI — Production Readiness Checklist
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies  
**Repo:** chichi-lyman/saphira-ai

Saphira is **architecturally complete in code** when the three benchmarks below pass in *your* live environment. This document separates **what the mono-repo provides** from **what only you can verify on device / cloud**.

---

## Benchmark 1 — Backend & Infrastructure

| Criterion | Repo status | Your live check |
|-----------|-------------|-----------------|
| Active database (Supabase v0-saphira-ai or equivalent) | Optional vector path documented; local NovaAethrea JSON memory ships without Supabase | Unpause project; confirm embeddings + conversation logs write |
| CI/CD green (Core Protocol / saphira-core-ci) | Workflows present: `.github/workflows/ci.yml`, `saphira-core-ci.yml` | Actions tab → latest run **green**; fix any remaining pytest/path issues |
| Deploy (Vercel / gateway) | Not auto-verified from repo alone | Production URL healthy; no failed deploys |
| Sub-300ms audio/vision path | Architecture targets documented (dual pipeline, ADA bridge) | Measure RTT through your encrypted proxy under real load |

**Pass rule:** DB live + CI green + deploy healthy + latency measured under 300ms for the critical path you care about (or documented exception).

---

## Benchmark 2 — Multi-Agent Interoperability

| Criterion | Repo status | Your live check |
|-----------|-------------|-----------------|
| Agent handshakes (Saphira → Zero / Two / Aura / Reign / Aethrea / Lyra) | Orchestrator chain, roles, equilibrium, classification in `src/` | Run smoke / stress tests; no deadlock on sample intents |
| Clear state delegation | `safe_run`, status codes, dual pipeline redaction | Trace one L1 and one L2 request end-to-end |
| Tool & webhook execution (n8n / Make) | Sales swarm + Make forward + Stripe webhooks in sibling patterns; Make blueprint in docs | POST test webhook; payload returns to Saphira/CRM |

**Pass rule:** One full chain succeeds (intent → agents → tool/webhook → Samantha public reply) without failed loops.

---

## Benchmark 3 — Client & Handshake

| Criterion | Repo status | Your live check |
|-----------|-------------|-----------------|
| OpenClaw (or device gateway) WebSocket | Not bundled as OpenClaw brand; use your gateway + backend WS | Authenticated WS connects and stays up |
| Default assistant override | `VoiceInteractionService` stack + `AssistantChannel` + overlay | Settings → Digital assistant = Saphira; gesture opens overlay |
| Context capture + real-time response | Overlay + autonomy gate + TTS profile | Speak → response with Chelsea voice path; L1 shows Confirm |

**Pass rule:** Assistant shortcut opens Saphira, captures input, returns a live agent-backed reply without crash.

---

## Honest scorecard (code vs production)

| Area | Code in mono-repo | Production-ready only after live pass |
|------|-------------------|----------------------------------------|
| Core agents + taxonomy + L1–L3 | Yes | Yes, after CI + device tests |
| Samantha dual pipeline | Yes | Yes, with LLM keys |
| Gemini-style Android shell | Scaffold yes | Yes, after manifest merge + default app |
| Matter / HA | Connector yes | Yes, with HA URL/token |
| Supabase vectors | Optional / external | Yes, when project unpaused + wired |
| OpenClaw-named gateway | External product | Your handshake test |
| Sub-300ms guarantee | Target, not measured here | Your proxy metrics |

---

## Minimum commands before you call it “complete”

```bash
# Repo
cd saphira-ai
pip install -r requirements.txt  # if present
pytest -q || python -m pytest tests/ -q

# CI: push and confirm GitHub Actions green

# Device
# 1. Merge AndroidManifest snippets
# 2. Set default assistant to Saphira AI
# 3. Grant mic + overlay
# 4. Wake word or assistant gesture → overlay → one L2 command + one L1 confirm flow
```

---

## Definition of done (Chelsea Megan Woods)

Saphira is **production-ready** when:

1. **Integration** — DB + CI + deploy + latency bar met  
2. **Continuous deployment** — main stays green; releases ship without manual heroics  
3. **Orchestration** — agents hand off cleanly; webhooks return data; assistant UX works on your phone  

Until those three are checked in *your* environment, treat the system as **architecture-complete, environment-pending**.
