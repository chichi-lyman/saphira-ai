# Saphira AI Roadmap

High-level direction for making life 1% easier, calmer, and less stressful every day.

Status key: **Done** · **In progress** · **Planned** · **Idea**

---

## Near term

| Item | Status | Notes |
|------|--------|-------|
| Stricter CI (lint + tests + coverage artifact) | In progress | See `.github/workflows/` |
| Issue & PR templates | In progress | Under `.github/` |
| README badges + clearer quick start | In progress | |
| Public chat + avatar surface stability | In progress | Live demo: https://saphira-delta.vercel.app |
| Document API surfaces (`/chat`, `/nodes`, `/avatar`, IoT) | Planned | OpenAPI already at `/docs` when server runs |

## Core platform

| Item | Status | Notes |
|------|--------|-------|
| Multi-agent routing | Done | Task delegation across specialized agents |
| Persistent memory layer | Done / ongoing | Context + preferences across sessions |
| Resilience patterns (circuit breaker, retry, bulkhead) | Done | |
| WebGPU acceleration path | Planned / experimental | Browser-native acceleration where available |
| Health & metrics endpoints | Planned | |

## IoT & Nodes

| Item | Status | Notes |
|------|--------|-------|
| Media / appliances / lighting / smart bed / print / companion hubs | Done (scaffold) | Controllers wired in `main.py` |
| Saphira Nodes registry (eyes / ears / hands / screens) | In progress | OpenClaw-inspired companion surface |
| Real device integrations (Bluetooth, Wi-Fi, vendor APIs) | Planned | |
| Safe command policies & confirmations | Planned | |

## Avatar & persona

| Item | Status | Notes |
|------|--------|-------|
| Chelsea-look visual avatar (Grok Imagine) | In progress | `/avatar` surface |
| Avatar state tied to chat | In progress | |
| Richer emotional / situational expressions | Idea | |

## Clients

| Item | Status | Notes |
|------|--------|-------|
| Web demo (Vercel) | Done | https://saphira-delta.vercel.app |
| Flutter / Android client | In progress | Repo includes Flutter + Android paths |
| Termux / edge setup script | Done | `setup-termux.sh` |

## Community & DX

| Item | Status | Notes |
|------|--------|-------|
| Contributing guidelines | Done (basic) | Expand as needed |
| Labels + triage workflow | Planned | |
| Architecture deep-dive doc | Planned | Under `docs/` |
| Demo video / GIF in README | Idea | |

---

## How to influence the roadmap

1. Open a **Feature request** issue using the template.
2. Comment on existing issues with use cases.
3. Submit PRs for small, well-scoped improvements.

*Last updated: 2026-08-06 · Architect: Chelsea Megan Woods*
