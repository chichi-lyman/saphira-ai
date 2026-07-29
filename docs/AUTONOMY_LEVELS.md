# Autonomy Levels — Saphira & Industry Reference
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

There is no single universal count of autonomy levels. The number depends on the **framework**. Saphira uses a **3-level** operational safety model; industry standards use other scales for vehicles and software agents.

---

## 1. Saphira Multi-Agent Architecture — **3 Levels**

Designed for task safety and human-in-the-loop gating.

| Level | Name | Behavior | Typical use in Saphira |
|-------|------|----------|-------------------------|
| **L1** | Confirm First / Hard Gate | Zero execution autonomy. Agent drafts or plans only; **explicit human approval** required before run. | Security, lock/unlock, payments, cold outreach, prod migrations |
| **L2** | Supervised / Bounded | Runs automatically **inside preset rules or sandboxes**; alerts on material changes. | Coding in sandbox, UI drafts, smart-home adjustments, Lyra local render |
| **L3** | Silent Background | Full background autonomy without per-step prompts; notify on completion or critical exception. | Memory/vector ingestion, telemetry indexing, Aura context synthesis, NovaReign/Aethrea equilibrium scoring |

### Defaults (Woods AI Studio)

- Sales email send, unlock, payment → **L1**
- Agent Zero code in sandbox, Matter lights/scenes → **L2**
- NovaAethrea history, Aura perception → **L3**

Code: `src/core/agent_classification.py` (`AutonomyLevel`, `action_autonomy`, `requires_human_confirmation`).

---

## 2. Industry Standard Models

### Autonomous driving — SAE J3016 — **6 levels (0–5)**

| Level | Name | Summary |
|-------|------|--------|
| 0 | No Automation | Human does all the work |
| 1 | Driver Assistance | Single feature help (e.g. adaptive cruise) |
| 2 | Partial Automation | Steering + acceleration together; human monitors |
| 3 | Conditional Automation | System drives in defined conditions; human ready to take over |
| 4 | High Automation | No human intervention inside defined zones/ODD |
| 5 | Full Automation | Self-driving under all conditions |

### AI agent software scales — **5 to 7 levels**

**OpenAI-style agent scale (5 levels, conceptual):**  
L1 conversational bots → L2 reasoners → L3 multi-step executors → L4 innovators → L5 full organizations.

**Bessemer-style AI scale (7 levels, L0–L6, conceptual):**  
From simple prompt–response (L0) up to agents that manage entire teams of other agents (L6).

These software scales measure **task complexity and delegation**, not the same as Saphira’s **safety gate** model.

---

## 3. Summary

| Context | Total levels | Range | Core focus |
|---------|--------------|-------|------------|
| **Saphira architecture** | **3** | L1–L3 | Operational safety & human-in-the-loop gating |
| **SAE automotive** | **6** | 0–5 | Vehicle / road automation |
| **General AI software scales** | **5–7** | L0/L1–L5/L6 | Task complexity, delegation, multi-agent coordination |

---

## 4. Design rule for Saphira

Map every **intent** to a Saphira L1/L2/L3 requirement.  
Do not conflate SAE Level 4 “no human in the loop” with Saphira L3: Saphira L3 is still bounded by Agent Two, Nova Reign policy, and emergency lockdown. Irreversible real-world actions stay L1 unless the user has explicitly pre-authorized a narrow rule.
