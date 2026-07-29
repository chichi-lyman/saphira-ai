# Saphira Agent Classification System
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira agents are classified on **three dimensions** beyond personal productivity:

1. Specialized application domains (verticals)
2. Foundational architectural types (classic CS taxonomy)
3. Operational autonomy levels

This sits on top of `docs/AI_AGENT_ANATOMY.md` (model vs agent, pillars, loop).

---

## 1. Specialized Application Domains (Verticals)

| Domain | Purpose | Saphira mapping |
|--------|---------|-----------------|
| Personal finance / trading | Portfolio, spend, risk rules | Finance specialist agents (planned / extensible) |
| Health, longevity, wellness | Biometrics, recovery, routines | `biometric_stress`, lifestyle orchestrator |
| Creative / media production | Assets, edit, format | UI/UX & content specialists |
| Social / audience growth | Schedule, engage, qualify leads | Sales swarm + social connectors |
| Smart home / IoT / spatial | Climate, lights, security, presence | Aura + Matter/HA + Agent Zero |
| Personal security / privacy | Footprint, phishing, credentials | Agent Two + private vault |
| Learning / tutoring | Adaptive skill practice | Education specialists (extensible) |
| Executive / admin ops | Inbox, calendar, meeting follow-up | **Saphira Admin Co-Pilot (B2B flagship)** |

Vertical agents are **specialists** under the orchestrator. They share the same pillars and loop; only tools and policies differ.

---

## 2. Foundational Architectural Types

```
1. Simple Reflex        → fixed condition-action rules
2. Model-Based          → internal world state
3. Goal-Based           → multi-step plans toward targets
4. Utility-Based        → optimize among options (cost, speed, safety)
5. Learning             → improve from feedback / Circle of Life
6. Multi-Agent System   → collaborative swarm
7. Embodied             → sensors + actuators (phone, HA, Matter)
```

### How Saphira uses them

| Type | Where it appears |
|------|------------------|
| Simple reflex | Fast voice intent regex; some HA toggles |
| Model-based | NovaAethrea state + Aura room/entity model |
| Goal-based | Orchestrator task breakdown; scene expansion |
| Utility-based | LLM router fallbacks; scene vs single action choice |
| Learning | Self-healing stats, scene preference updates, optional federated prefs |
| Multi-agent | Full roster: Saphira + Zero + Two + Aura + Reign + Aethrea + domain agents |
| Embodied | Camera, mic, Matter devices, wearables |

Most production paths are **hybrid**: reflex for speed, model + goal for complex requests, multi-agent for safety and specialization.

---

## 3. Operational Autonomy Levels

| Level | Name | Behavior in Saphira |
|-------|------|---------------------|
| **L1** | Co-pilot / human-in-the-loop | Every sensitive step waits for the user |
| **L2** | Gated / semi-autonomous | Multi-step run OK; pause on send, unlock, pay, deploy |
| **L3** | Fully autonomous / proactive | Background monitoring; notify on completion or critical exception only |

### Default policy (Woods AI Studio)

- **Personal chat & drafts:** L1–L2 (user sees drafts; no silent external send)
- **Smart home non-sensitive:** L2–L3 (scenes after user-defined rules)
- **Lock / unlock / payments:** L1 or L2 with explicit confirmation (Agent Two)
- **Sales swarm outreach:** L1 (draft only until Chelsea approves)
- **B2B pilot runtime:** L2 inside client policy, never silent money movement

Autonomy is **per action type**, not a single global switch.

---

## 4. Classification API (code)

See `src/core/agent_classification.py`:

- `VerticalDomain` enum
- `ArchitectureType` enum
- `AutonomyLevel` enum
- `classify_core_agent(name)` → domain + architecture + default autonomy
- `action_autonomy(intent)` → required level for a given intent

---

## 5. Design rule

Every new Saphira agent must declare:

1. **Vertical** (which domain it serves)
2. **Architecture mix** (reflex / model / goal / utility / learning / MAS / embodied)
3. **Max autonomy level** allowed without human confirmation

Unclassified agents are treated as **L1 specialists** until reviewed by Nova Reign policy.
