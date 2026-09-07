# Nova Umbrella System Architecture & Governance Framework™

**Author:** Chelsea Megan Woods™ #ChelseaMeganWoods  
**Classification:** Core System Architecture & Ecosystem Specification  
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

---

## 1. Executive Summary & Product Intent

Saphira™ is engineered as a policy-gated, multimodal executive platform—moving beyond basic conversational chat to deliver direct, governed task execution. Operating as the primary interface within the Nova Umbrella™ ecosystem, Saphira processes multi-source context, dispatches execution graphs across dedicated agent infrastructure, and continuously refines outputs under strict real-time constraints.

### The Gemini-Parity Execution Target

The target operational model aligns with high-velocity multimodal reasoning, upgraded with deterministic governance:

```text
User → Saphira Interface → Multimodal Intent + Context → Executive Planner
  → Task Graph → Capability Registry → Worker Adapters → Verification → Memory → Output
```

Nova Umbrella adds what standard chat interfaces lack: **scored governance before side effects** and a **CEO (Saphira L2) vs back-office workers (L3)** split so the public interface never freely pays, deploys, or unlocks sensitive operations without **L1** approval.

---

## 2. Gemini Capabilities vs. Nova Governance Matrix

| Gemini Behavior | Functional Operational Target | Nova Governance & Equilibrium Gate |
|---|---|---|
| **Multimodal Context Processing** | Simultaneous ingestion and reasoning over text, code, images, audio, and documents in one unified thread context. | **Context Integrity Gate:** Input payloads are validated for schema compliance, payload boundaries, and safety policies prior to entering the planner. |
| **Direct Task Execution** | Native tool calling across connected APIs, IDEs, workspaces, and system channels returning structured results. | **L1/L3 Approval Gates:** Side-effects, financial mutations, code commits, and deployment actions require explicit user/L1 authorization. |
| **Iterative Refinement** | Continuous adaptation to changing specs, architecture rules, and constraints within long-horizon sessions. | **Equilibrium Scoring:** State evaluation (Reign/Aethrea) ensures agent drift is identified and re-aligned dynamically. |

---

## 3. Ecosystem Roster & Operational Architecture

```text
  +-----------------------------------------------------------------------+
  |                             USER INTERFACE                            |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  |                     SAPHIRA™ EXECUTIVE (L2 CEO)                        |
  |  - Ingests Context       - Generates Task Graphs                      |
  |  - Negotiates Intent     - Orchestrates L3 Workers                    |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  |                   NOVA UMBRELLA CORE (L1 GOVERNANCE)                  |
  |  - Non-Bypassable Safety Substrate   - Credential Access Control     |
  |  - Scored Equilibrium Engine         - State Persistence Ledger      |
  +-----------------------------------------------------------------------+
                                      |
        +-----------------------------+-----------------------------+
        |                             |                             |
        v                             v                             v
  +-----------+                 +-----------+                 +-----------+
  | WORKER L3 |                 | WORKER L3 |                 | WORKER L3 |
  | Code Engine |               | Workspace |                 | Security  |
  | & Deploy  |                 | Connectors|                 | Audit Gate|
  +-----------+                 +-----------+                 +-----------+
```

- **Saphira™ (Executive L2):** Public-facing CEO agent handling context ingestion, user negotiation, task graph generation, and orchestrating worker deployment.
- **Nova Umbrella Core (L1 Governance):** The non-bypassable safety substrate enforcing rate limits, credential access, approval gates, and state persistence.
- **Specialized Back-Office Workers (L3):** Purpose-built sub-agents tasked with isolated execution (code compilation, vulnerability analysis, document generation, API integration).

---

## 4. Complete Agent Roster

Every specialist serves a distinct role, mapped by **Vertical Domain**, **Architectural Mix**, and **Max Autonomy Level**.

### 4.1 Saphira — Brand Face & Primary Orchestrator

- **Vertical:** Executive Admin & Public Interface
- **Architectures:** Multi-Agent, Goal-Based, Utility-Based
- **Max Autonomy:** **L2** (Gated Execution)
- **Needs:** Intent router; brand/tone + preference vault; UI for L1 draft previews (email, financial gates)

### 4.2 NovaReign & NovaAethrea — Dual Equilibrium (Yang & Yin)

| Engine | Focus | Autonomy |
|--------|--------|----------|
| **NovaReign** (Yang) | Expansion, momentum, creative proposals, high-velocity options | L3 |
| **NovaAethrea** (Yin) | Constraint, risk, policy, edge cases, memory/scenes | L3 |

- **Vertical:** Governance, risk evaluation, learning & perception
- **Architectures:** Learning, Model-Based, Utility-Based (evaluator / critique pair)
- **Equilibrium mediator:**

```text
Final_Action_Score ≈ NovaReign_Score + NovaAethrea_Constraint
```

Action proceeds only when balance clears governance gates (and is not hard-blocked).

### 4.3 Aura — Perception & Context Engine

- **Vertical:** Learning & Perception
- **Architectures:** Learning, Multi-Agent, Reflex
- **Max Autonomy:** **L3** (silent background)
- **Needs:** Vector/embedding pipeline; telemetry ingestion; fast context retrieval for other agents

### 4.4 Agent Zero — Systems & Code Engineering

- **Vertical:** Technical Systems & Developer Ops
- **Architectures:** Goal-Based, Model-Based, Learning
- **Max Autonomy:** **L2** (gated sandbox)
- **Needs:** Code sandbox; GitHub / deploy tooling; **L1 hard gate** on production migrations and external server changes

### 4.5 Agent Two — Security & Boundary Enforcement

- **Vertical:** Security & Boundary
- **Architectures:** Reflex, Model-Based
- **Max Autonomy:** **L1** (hard gate)
- **Needs:** Zero-trust auth; threat logger; panic / lockdown endpoint to pause L2/L3 queues

### 4.6 Lyra — Creative Direction & Automation Design

- **Vertical:** Creative, Social & UI/UX Automation
- **Architectures:** Model-Based, Goal-Based
- **Max Autonomy:** **L2** (draft L1 / local render L2)
- **Needs:** Design/asset pipeline; Make/n8n social orchestrator; voice & style guide (dark-mode luxury tokens)

### System Summary Matrix

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

## 5. Equilibrium Math (Code Contract)

Implemented in `src/core/equilibrium.py`:

- **NovaReign score** raises action likelihood for priority, user request, creativity, and confidence.
- **NovaAethrea constraint** damps or hard-blocks sensitive intents (`unlock`, `payment`, `send_email`, `migrate`, `deploy_prod`) unless confirmed; applies deny lists and anomaly penalties.
- **Proceed** only if not hard-blocked and `final_action_score >= threshold` (default ~0.35).

Canonical handoff pipeline:

```text
Saphira (intent) → Aura (perception) → Agent Two (security)
  → Nova Reign (governance / expansion) → NovaAethrea (memory / constraint)
  → Agent Zero (execution)
```

Internal codenames are **not** exposed to end users; only Saphira’s persona is public.

---

## 6. Technical Roadmap to Gemini Parity

### Phase 1: Multimodal Ingestion Pipeline

- [ ] Implement single-turn pipeline accepting raw audio, image binary streams, multi-page PDFs, and code schemas simultaneously into the Executive Planner context.
- [ ] Configure streaming WebSockets with voice interruption hooks for real-time edge and web interaction.

### Phase 2: Production Action Wiring

- [ ] Finalize live OAuth2 refresh token flows for Google Workspace and Microsoft Graph adapters.
- [ ] Wire direct git repository manipulation tools bounded by L1 branch-protection checks.

### Phase 3: Transactional State Ledger

- [ ] Enable persistent thread memory ensuring multi-turn policy and architectural changes update the active task graph without losing session state.

Detailed task breakdown: [`docs/GEMINI_PARITY_IMPLEMENTATION_PLAN.md`](GEMINI_PARITY_IMPLEMENTATION_PLAN.md)

---

## 7. Code Anchors

- `src/core/agent_classification.py` — domains, architectures, autonomy
- `src/core/equilibrium.py` — Reign + Aethrea score mediator
- `src/agents/core_agents.py` — Saphira, Zero, Two, Aura, Reign, Aethrea
- `src/agents/lyra.py` — Lyra creative agent
- `schemas/landing_page_chelsea_io.json` — chelsea.io landing page schema

---

## 8. Plain-English Summary

Nova Umbrella™ is like a high-tech corporate office for AI. Chelsea Megan Woods™ designed Saphira-AI™ as the friendly CEO who talks to the public while a hidden team of specialized workers handles the heavy lifting.

- **Saphira is the Front Desk:** the only voice the user talks to. She takes requests, passes them to the back office, and returns results.
- **Gas Pedal and Brakes (NovaReign & NovaAethrea):** before major decisions, expansionary scoring and policy constraints are combined so speed does not override safety.
- **Behind-the-Scenes Specialists:** Aura, Agent Zero, Agent Two, Lyra, and other workers handle perception, code, security, and creative work.
- **Safety First:** Saphira cannot unilaterally run critical side effects (payments, production deploys, unlocks) without explicit L1 confirmation when policy requires it.
