# The Weaver Everyday — Technical Blueprint

**Copyright © 2026 Chelsea Megan Woods**  
**Parent:** [THE_WEAVER_EVERYDAY.md](./THE_WEAVER_EVERYDAY.md)

Exhaustive architectural blueprint for the four everyday functions. Paradigm: flexible **cognitive mirror**, not rigid automation.

---

## 1. Choice Mapper

```
[Chaotic Mind-Dump]
        → Semantic Entity Extraction (facts vs emotions)
        → Topological Graphing (dependency paths)
        → Predictive Scenario Modeling (ripple UI)
        → Net Reality Ledger (clarity, not prescription)
```

| Stage | Technical role |
|-------|----------------|
| Semantic entity extraction | Map unstructured text/voice onto localized vectors; split Objective Parameters (money, hours, distance) from Subjective Variables (fear, guilt, nostalgia) |
| Topological graphing | Dependency edges (Commute → Sleep → Hobbies) on the user’s life map |
| Predictive scenario modeling | Path slider updates calculated lifestyle outcomes under current constraints |

**Why it works:** Offloads chaotic thought to a structured graph; frees working memory from anxiety loops.

**Runtime:** `ChoiceMapper` in `weaver_everyday.py` (matrix + tradeoff nodes; full NLP/voice adapters plug in via Aura).

---

## 2. Crisis Synthesizer

```
[Bills / Pics / Quotes]
        → Multi-Modal Intake (OCR, screenshots)
        → Cross-Disciplinary Risk Triage (physical vs financial)
        → Script & Logistics Engine
        → 30-Day Action Path
```

| Stage | Technical role |
|-------|----------------|
| Multi-modal intake | OCR on bills/quotes; bank context; optional smart-home codes (Aura perception) |
| Risk triage | Score physical degradation vs penalty risk; safe deferral windows |
| Script engine | Negotiation / consumer-rights **stubs** (Lexis-aware; not legal advice) |

**Why it works:** Objective buffer when prefrontal capacity is impaired by stress.

**Runtime:** `CrisisSynthesizer`; Agent Two sandboxes document intake; no autonomous payments.

---

## 3. Energy Tracker

```
[User State: N% brainpower]
        → Cognitive Load Tagging (EF cost, friction, dopamine velocity)
        → Biometric/self-report calibration
        → Frictionless Micro-Step Slicing
        → Momentum Mode UI
```

| Tag | Meaning |
|-----|--------|
| Executive Function Cost | Mental organization required |
| Physical Friction | Movement / setup cost |
| Dopamine Velocity | Speed to a sense of completion |

**Why it works:** Targets task initiation; lowers barrier so avoidance loops are bypassed without draining residual energy.

**Runtime:** `EnergyTracker` energy bands + eligibility filter.

---

## 4. Symptom Detective

```
[Casual Notes] + [Wearables / Environment]
        → Asynchronous Ingestion
        → Multi-Stream Time-Series Fusion
        → Cross-Correlation (time-delay windows)
        → Hypothesis + Micro-Experiment
```

| Stream | Examples |
|--------|----------|
| Casual notes | “3 PM wiped out after lunch” |
| Wearables | Sleep architecture, HRV, steps |
| Environment | Optional weather / pressure |

**Why it works:** Bypasses retrospective bias with objective co-occurrence across delays.

**Runtime:** `SymptomDetective`; consent-gated biometrics; exploratory confidence only.

---

## Shared invariants

- Saphira-only surface; secret-mask on internal agents
- Commercial / external / medical / legal: informational + policy gates
- NovaAethrea persists life-map context across sessions when user allows
- Aura owns multi-modal perception; Lyra owns correlation stats

## Related

- [THE_WEAVER_EVERYDAY_MECHANISMS.md](./THE_WEAVER_EVERYDAY_MECHANISMS.md)
- [THE_WEAVER_WEEKLY_TIMELINE.md](./THE_WEAVER_WEEKLY_TIMELINE.md)
- `src/orchestration/weaver_everyday.py`
