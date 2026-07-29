# Autonomy Levels — Saphira & Industry Reference
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

## 1. Saphira — **3 Levels** (operational safety)

| Level | Name | Behavior | Examples |
|-------|------|----------|----------|
| **L1** | Confirm First / Hard Gate | Draft/plan only until explicit human OK | Unlock, payment, send email, cold outreach, prod migrate |
| **L2** | Supervised / Bounded | Auto within rules/sandbox; alert on changes | Sandbox code, UI draft, lights/scenes |
| **L3** | Silent Background | No per-step prompt; notify on done/critical | Vector ingest, telemetry, context synthesis |

Flutter: `lib/services/autonomy_gate.dart`  
Python: `src/core/agent_classification.py`, `src/core/autonomy_levels.py`

**Overlay rule:** Wake word may open the sheet; it must **not** auto-run L1 actions.

---

## 2. SAE J3016 — Level 4 vs Level 5 (vehicles)

| SAE Level | Meaning |
|-----------|--------|
| **4 High Automation** | System handles driving **without human** but **only inside** a defined operational design domain (geo, weather, mapped area). |
| **5 Full Automation** | System handles **all** conditions, **everywhere** — human not expected as fallback. |

### Saphira mapping (analogy only)

- SAE 4 ≈ bounded high autonomy **inside** user policy (home, allowed scenes) → closest to **Saphira L2–L3 with rules**
- SAE 5 ≈ unbounded physical autonomy → **not** a Saphira product goal

**Saphira L3 is not SAE Level 5.** Background software jobs ≠ full unsupervised control of locks, money, or production systems.

---

## 3. Other software scales (reference)

- OpenAI-style agent scales (~5 levels): bots → reasoners → multi-step agents → innovators → orgs
- Bessemer-style (~7 levels L0–L6): prompts → agents managing agent teams

These measure **capability complexity**, not Saphira’s **safety gates**.

---

## 4. Summary

| Framework | Levels | Focus |
|-----------|--------|--------|
| Saphira | L1–L3 | Human-in-the-loop safety |
| SAE | 0–5 | Driving automation |
| AI software scales | 5–7 | Task/delegation complexity |
