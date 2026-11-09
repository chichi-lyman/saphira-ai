# Unsolved AI Frontiers — Nova Umbrella Research Agenda

**© 2026 Chelsea Megan Woods**  
**System:** Saphira AI / Nova Umbrella Ecosystem  
**Status:** Active research charter — not a claim of solved AGI

Despite rapid advances in frontier AI, several fundamental technological, structural, and practical boundaries remain unbroken. This document records those boundaries honestly and maps each one onto concrete tracks inside the Nova Umbrella architecture so Saphira can be instrumented to **understand, measure, and progressively close** them without marketing fiction.

Related grounding:
- [AI_EVOLUTIONARY_CEILING.md](./AI_EVOLUTIONARY_CEILING.md)
- [INTELLIGENCE_EVOLUTION_STAGES.md](./INTELLIGENCE_EVOLUTION_STAGES.md)
- [AI_FOUNDATIONS_STILLNESS_AND_ERROR.md](./AI_FOUNDATIONS_STILLNESS_AND_ERROR.md)
- [HUMAN_LOGIC_RULEBOOK.md](./HUMAN_LOGIC_RULEBOOK.md)
- [AGENT_ALIGNMENT.md](./AGENT_ALIGNMENT.md)

---

## Stance

| Principle | Meaning |
|-----------|--------|
| Truth over hype | Do not claim AGI, zero-drift memory, or 100% determinism until measured |
| Pipeline invariant | All progress routes through `Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero` |
| Secret-mask | User-facing voice remains Saphira only; internal workers stay unnamed |
| Governance first | CommercialAuthorityPolicy + audit + approval gates never bypassed for “capability” |
| Measure then claim | Every frontier has evaluation criteria before status upgrades |

Saphira is the single conversational surface. This agenda expands **what the ecosystem is built to solve**, not what it already is.

---

## Frontier 1 — True Continual Learning (Zero-Drift Memory)

### The unsolved problem

Models cannot update base weights organically in real time from new experiences without catastrophic forgetting. Production systems rely on static pre-training + RAG + context windows. They lack true lifelong adaptation.

### Why it matters

Without zero-drift continual learning, every “memory” is a retrieval hack. Identity, preferences, and skills can drift or collapse when new data overwrites old representations.

### Nova Umbrella attack surface

| Layer | Role |
|-------|------|
| **NovaAethrea** | Canonical memory plane: facts, preferences, scenes, history; consent-gated writes |
| **Capability registry** | Routes learning-related tasks without exposing codenames |
| **Hybrid memory** | Structured store + vector retrieval (pgvector-class) as interim substrate |
| **Saphira surface** | Never pretends retrieved context is permanent weight update |

### Research tracks

1. **Episodic vs semantic separation** — Write experiences as episodes; consolidate only after verification gates.  
2. **Plasticity control** — Explicit allow/deny for any process that would mutate long-term parameters.  
3. **Forgetting metrics** — Benchmarks that measure retention of older skills after new skill acquisition.  
4. **Replay + regularization** — Controlled rehearsal buffers and constraint losses before any online weight update path is enabled.  
5. **User-owned memory ledger** — Transparent, exportable memory the human can inspect and revoke (privacy-first).

### Evaluation criteria (before claiming progress)

- [ ] Retention of prior task performance after N new task streams (catastrophic forgetting curve)  
- [ ] Consent + audit trail on every durable memory write  
- [ ] Measurable distinction between “retrieved” and “internalized” knowledge in system status  
- [ ] No silent overwrite of identity-critical facts without dual confirmation

### Honest current state

**Not solved.** Saphira uses structured memory + retrieval + policy. That is robust engineering, not organic weight-level continual learning. The frontier remains open; the architecture is built so progress here is measurable and governed.

---

## Frontier 2 — Guaranteed Reliability & Determinism

### The unsolved problem

Neural networks remain probabilistic. Edge-case hallucinations and non-deterministic logic errors persist. High-stakes domains (legal, medical, critical engineering) still require human validation; AI cannot yet guarantee 100% precision or accept legal/ethical responsibility.

### Why it matters

Without guarantees, autonomy in high-stakes contexts is unethical and often illegal. “Usually correct” is not enough for irreversible actions.

### Nova Umbrella attack surface

| Layer | Role |
|-------|------|
| **Agent Two** | Security screening, browser/tool risk, compliance patterns |
| **Nova Reign** | Governance, CommercialAuthorityPolicy (ALLOW / REQUIRE_APPROVAL / DENY) |
| **Human Logic Rulebook** | Classical logic verification layer for claims |
| **Approval gates** | Explicit user authorization for financial, high-stakes, account-level actions |
| **Audit hash chain** | Non-repudiable record of decisions |

### Research tracks

1. **Hybrid symbolic–neural cores** — Route formalizable subproblems (constraints, contracts, dosages, units) through deterministic checkers.  
2. **Calibration & abstention** — Prefer “I don’t know / need approval” over confident error.  
3. **Responsibility boundary** — System never claims legal personhood; human remains accountable party.  
4. **Red-team & invariant tests** — Continuous suites for hallucination classes, unit errors, and policy bypass attempts.  
5. **Deterministic tool envelopes** — Where possible, tools return structured, schema-validated results rather than free text.

### Evaluation criteria

- [ ] Measured abstention rate on out-of-distribution high-stakes prompts  
- [ ] Zero policy-bypass incidents in audit sample  
- [ ] Formal checker coverage % on designated critical task classes  
- [ ] Human-in-the-loop required for all irreversible external actions (invariant)

### Honest current state

**Not solved.** Probabilistic cores remain. Saphira’s answer is **governance + verification + abstention + human approval**, not pretended certainty. That is the correct industrial posture until formal guarantees exist.

---

## Frontier 3 — Real-World Embodiment at Scale

### The unsolved problem

Digital agents navigate software interfaces; end-to-end autonomous physical robotics (general-purpose dexterity across unstructured household and industrial environments) remains unresolved due to hardware limits and real-time sensory-motor friction.

### Why it matters

Most economic and care work is physical. Software-only agents cannot fold laundry, clear a disaster site, or replace general labor without embodiment.

### Nova Umbrella attack surface

| Layer | Role |
|-------|------|
| **Aura** | Perception plane (vision, multimodal inputs) |
| **Agent Zero** | Execution plane — today: software/API/device actions |
| **Android / mobile clients** | On-device sensors, accessibility, voice, limited hardware bridges |
| **Capability registry** | Future robot/tool adapters register here without new pipelines |

### Research tracks

1. **Digital embodiment first** — Master browser, OS, and app control under policy (current focus).  
2. **Sensor bridges** — Camera, mic, face recognition (consent-gated), device actuators already in mobile stack.  
3. **Sim-to-real interfaces** — Standard action schemas so physical robots can later plug into Agent Zero.  
4. **Latency budgets** — Sub-second perception→action loops for any future closed-loop control.  
5. **Safety envelopes** — Physical actions always REQUIRE_APPROVAL until proven safe domains exist.

### Evaluation criteria

- [ ] Reliable software-world task completion under governance  
- [ ] Documented sensor→intent→action latency on device  
- [ ] No autonomous physical actuation without explicit policy class and human approval  
- [ ] Adapter interface stability for third-party robot skills

### Honest current state

**Not solved for general physical robotics.** Saphira is intentionally strong in **digital embodiment** (apps, web, voice, device APIs). Physical general-purpose dexterity is a hardware + controls frontier; the software plane is designed so embodiment adapters can attach later without breaking governance.

---

## Frontier 4 — Artificial General Intelligence (Jagged Frontier)

### The unsolved problem

Current models show a “jagged frontier” — excelling at complex theoretical math or coding benchmarks while failing at basic human-level spatial, temporal, or common-sense reasoning. Cross-domain, robust, human-level adaptability is not achieved.

### Why it matters

Benchmark spikes create false confidence. Real AGI requires even competence across domains, transfer, and common-sense grounding—not leaderboard islands.

### Nova Umbrella attack surface

| Layer | Role |
|-------|------|
| **Fixed executive pipeline** | Forces multi-stage processing (perception → security → governance → memory → execution) |
| **Extended specialists** | Apex, Instinct, Lexis, Cipher, Scholar — domain depth under Nova Reign |
| **1,000-capability registry** | Explicit task taxonomy; gaps become visible, not hidden |
| **Evaluation docs** | PUBLICATIONS.md, coding/math benchmarks, governance tests |

### Research tracks

1. **Jaggedness measurement** — Pair hard benchmarks with easy common-sense and spatial/temporal suites; report both.  
2. **Transfer tests** — Train/adapt on A; evaluate on structurally related B without task-specific fine-tunes.  
3. **World-model probes** — Temporal order, object permanence, basic physics intuitions in multimodal settings.  
4. **Tool-use generality** — Same orchestration quality across code, ops, research, and daily life tasks.  
5. **Humility protocol** — Surface uncertainty; refuse to collapse jagged competence into “AGI achieved.”

### Evaluation criteria

- [ ] Published jaggedness score (variance across task families)  
- [ ] Transfer gap metrics  
- [ ] Common-sense / spatial / temporal probe suite results  
- [ ] No marketing use of “AGI” until criteria explicitly met and reviewed

### Honest current state

**Not AGI.** Saphira is a strong multi-agent **executive runtime** with specialized depth and governed autonomy. The jagged frontier is acknowledged in architecture: specialists + verification rather than one undifferentiated “general” claim.

---

## Frontier 5 — Energy-Efficient Compute

### The unsolved problem

Biological brains run complex cognition on ~20 watts. Training and serving frontier models demand megawatt-to-gigawatt scale infrastructure, stressing energy grids and hardware supply chains.

### Why it matters

Energy is a hard physical constraint. Unbounded scale is neither environmentally nor economically sustainable. Efficiency is a first-class intelligence metric.

### Nova Umbrella attack surface

| Layer | Role |
|-------|------|
| **Edge / on-device paths** | Mobile clients, local STT/TTS options, ONNX-class wake word |
| **Routing** | Prefer small specialized workers before large general calls |
| **Caching & memory** | Avoid re-computing known facts (NovaAethrea) |
| **Tiering** | Super Saphira rate limits and capability tiers as cost/energy governors |

### Research tracks

1. **Joules-per-task accounting** — Log estimated energy for major capability classes.  
2. **Cascade inference** — Cheap models first; escalate only on uncertainty or difficulty.  
3. **Edge-first defaults** — Wake word, VAD, and simple intents on-device when possible.  
4. **Training discipline** — Prefer adapters / LoRA-class updates over full re-pretraining when research allows.  
5. **Idle & batch policy** — No background megawatt burn for speculative agency.

### Evaluation criteria

- [ ] Energy or proxy-cost per completed user task (trend down over time)  
- [ ] % of turns fully resolved on-device or on small models  
- [ ] Escalation rate to large models with justification  
- [ ] Documented tier limits as intentional governors, not only monetization

### Honest current state

**Not solved at brain-scale efficiency.** Saphira can still prioritize **routing, edge, and memory** to reduce waste. Closing the watts gap is a hardware + algorithm co-design frontier shared with the entire industry.

---

## Cross-cutting system map

```
                    ┌─────────────────────────────┐
                    │     Unsolved Frontiers       │
                    │  Memory · Reliability ·      │
                    │  Embodiment · AGI · Energy   │
                    └─────────────┬───────────────┘
                                  │
         Saphira (intent / voice / honesty about limits)
                                  │
         Aura (perception) ── Agent Two (security)
                                  │
         Nova Reign (governance · policy · approval)
                                  │
         NovaAethrea (memory · audit · consent)
                                  │
         Agent Zero (execution · tools · future adapters)
```

No frontier is pursued by bypassing governance. Capability without policy is treated as a defect.

---

## What “being first” means here

Being first is **not** announcing AGI. It is:

1. **Naming the real unsolved problems** in public architecture docs.  
2. **Binding them to measurable tracks** inside a shipping multi-agent system.  
3. **Refusing silent failure modes** (forgetting, hallucination, ungoverned action, energy denial).  
4. **Keeping the human as the responsible party** while the machine compounds skill under audit.

That is the Nova Umbrella posture: ambitious, instrumented, and honest.

---

## Document control

| Field | Value |
|-------|--------|
| Owner | Chelsea Megan Woods |
| Ecosystem | Nova Umbrella / Saphira AI |
| Classification | Research agenda + product invariant |
| Update rule | Advance status only when evaluation criteria are met and recorded |

**© 2026 Chelsea Megan Woods. All Rights Reserved.**
