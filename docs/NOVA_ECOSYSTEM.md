# Nova Ecosystem — Complete Agent Roster
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Every specialist serves a distinct role, mapped by **Vertical Domain**, **Architectural Mix**, and **Max Autonomy Level**.

---

## 1. Saphira — Brand Face & Primary Orchestrator

- **Vertical:** Executive Admin & Public Interface
- **Architectures:** Multi-Agent, Goal-Based, Utility-Based
- **Max Autonomy:** **L2** (Gated Execution)
- **Needs:** Intent router; brand/tone + preference vault; UI for L1 draft previews (email, financial gates)

## 2. NovaReign & NovaAethrea — Dual Equilibrium (Yang & Yin)

| Engine | Focus | Autonomy |
|--------|--------|----------|
| **NovaReign** (Yang) | Expansion, momentum, creative proposals, high-velocity options | L3 |
| **NovaAethrea** (Yin) | Constraint, risk, policy, edge cases, memory/scenes | L3 |

- **Vertical:** Governance, risk evaluation, learning & perception
- **Architectures:** Learning, Model-Based, Utility-Based (evaluator / critique pair)
- **Equilibrium mediator:**  
  `Final_Action_Score ≈ NovaReign_Score + NovaAethrea_Constraint`  
  Action proceeds only when balance clears governance gates.

## 3. Aura — Perception & Context Engine

- **Vertical:** Learning & Perception
- **Architectures:** Learning, Multi-Agent, Reflex
- **Max Autonomy:** **L3** (silent background)
- **Needs:** Vector/embedding pipeline; telemetry ingestion; fast context retrieval for other agents

## 4. Agent Zero — Systems & Code Engineering

- **Vertical:** Technical Systems & Developer Ops
- **Architectures:** Goal-Based, Model-Based, Learning
- **Max Autonomy:** **L2** (gated sandbox)
- **Needs:** Code sandbox; GitHub / deploy tooling; **L1 hard gate** on production migrations and external server changes

## 5. Agent Two — Security & Boundary Enforcement

- **Vertical:** Security & Boundary
- **Architectures:** Reflex, Model-Based
- **Max Autonomy:** **L1** (hard gate)
- **Needs:** Zero-trust auth; threat logger; panic / lockdown endpoint to pause L2/L3 queues

## 6. Lyra — Creative Direction & Automation Design

- **Vertical:** Creative, Social & UI/UX Automation
- **Architectures:** Model-Based, Goal-Based
- **Max Autonomy:** **L2** (draft L1 / local render L2)
- **Needs:** Design/asset pipeline; Make/n8n social orchestrator; voice & style guide (dark-mode luxury tokens)

---

## System Summary Matrix

| Agent | Core Domain | Architecture | Autonomy | Operational Focus |
|-------|-------------|--------------|----------|-------------------|
| **Saphira** | Executive Admin | Multi-Agent / Goal | **L2** | Face, orchestrator, UI |
| **NovaReign** | Governance (Yang) | Utility / Learning | **L3** | Expansion, proposals |
| **NovaAethrea** | Governance (Yin) | Model / Critique | **L3** | Constraint, memory, policy |
| **Aura** | Perception | Learning / Reflex | **L3** | Context, telemetry |
| **Agent Zero** | Developer Ops | Goal / Model | **L2** | Code, sandbox, deploy |
| **Agent Two** | Security | Reflex / Model | **L1** | Auth, lockdown |
| **Lyra** | Creative & UI | Goal / Model | **L2** | Design, social, assets |

---

## Code anchors

- `src/core/agent_classification.py` — domains, architectures, autonomy
- `src/core/equilibrium.py` — Reign + Aethrea score mediator
- `src/agents/core_agents.py` — Saphira, Zero, Two, Aura, Reign, Aethrea
- `src/agents/lyra.py` — Lyra creative agent
