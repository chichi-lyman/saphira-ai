# The Weaver — Everyday Life Synthesis

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai / Nova Umbrella  
**Parent:** [THE_WEAVER.md](./THE_WEAVER.md)

The Weaver’s core mechanism—connecting hidden dots and adjusting context—becomes a **practical problem-solving companion** for everyday struggles. It does not return generic listicles; it builds plans mapped to the user’s real constraints.

Saphira remains the only user-facing identity. Everyday Weaver modes run as synthesis workflows behind the fixed pipeline.

---

## Strategic advantage

| Standard chatbots | The Weaver (everyday) |
|-------------------|------------------------|
| Generic instructions you could have googled | Custom plan mapped to unique constraints |
| Expects clean, logical questions | Accepts venting, rants, chaotic dumps—then organizes |
| Forgets the big picture between sessions | Connects budget, health, time, and goals into a unified life map |

---

## 1. Choice Mapper — overcoming decision paralysis

**Problem:** Stressful life choices (e.g. higher-pay job + commute vs remote but boring) overload pros, cons, and anxiety.

**What it does:** Accepts raw thoughts, feelings, and numbers; structures a **Dynamic Choice Matrix**.

**How:** Highlights hidden trade-offs with cause-and-effect mapping (time, money, stress, timelines)—without dictating the decision.

**Example output shape:**
- Options as nodes
- Trade-off edges (hours, savings %, stress metric, timeline delta)
- Visual matrix: clarity over prescription

**Capability:** `weaver.choice_map`  
**Runtime:** `ChoiceMapper` in `src/orchestration/weaver_everyday.py`

---

## 2. Crisis Synthesizer — sudden financial & domestic chaos

**Problem:** Multiple shocks at once (car, water heater, medical bill) with limited savings.

**What it does:** Emergency triage coordinator; accepts quotes, estimates, bank context (and photo/OCR hooks via Aura).

**How:** Cross-references urgency (structural risk vs deferrable), builds a **30-Day Financial Survival Path**, budget shifts, negotiation script stubs, DIY vs pro scheduling.

**Capability:** `weaver.crisis_synth`  
**Runtime:** `CrisisSynthesizer`

**Policy:** Financial and medical advice is informational; no autonomous payments; commercial/external actions stay gated.

---

## 3. Energy Tracker — executive dysfunction & burnout

**Problem:** Huge to-do list, near-zero capacity; rigid calendars make it worse.

**What it does:** **Energy-Adaptive To-Do Grid**—organize by cognitive energy type, not only clock slots.

**How:** User reports energy (e.g. “10% brainpower”); Weaver filters the life map to the smallest viable next action that builds momentum without draining residual capacity.

**Capability:** `weaver.energy_track`  
**Runtime:** `EnergyTracker`

---

## 4. Symptom Detective — chronic patterns & habit tuning

**Problem:** Ongoing fatigue/fog; normal labs; manual journaling is too heavy.

**What it does:** Passive pattern-recognition over casual notes + optional wearable data.

**How:** After enough samples, surfaces non-obvious correlations and a **low-effort experiment** for the next week—not a diagnosis.

**Capability:** `weaver.symptom_detect`  
**Runtime:** `SymptomDetective`

**Policy:** Not medical advice; pattern hypotheses only; biometric data requires consent (Agent Two).

---

## Agent map (everyday modes)

| Agent | Choice Mapper | Crisis Synthesizer | Energy Tracker | Symptom Detective |
|-------|---------------|--------------------|----------------|-------------------|
| Saphira | Decision intake, warm framing | Crisis intake, calm triage voice | Energy check-in UX | Casual note intake |
| Aura | Matrix visualization | Quote/photo OCR perception | Grid layout | Chart correlations |
| Agent Two | Sensitive-data gate | Financial doc sandbox | — | Biometric consent |
| Nova Reign | Trade-off DAG | 30-day plan orchestration | Task filter plan | Pattern job schedule |
| NovaAethrea | Preference + history | Budget snapshot memory | Energy baseline | Symptom log store |
| Agent Zero | Export matrix | Survival path artifact | Next-action card | Experiment card export |
| Lyra | Trade-off math | Urgency + cashflow stats | Energy vs task difficulty | Correlation stats |
| Lexis | — | Bill negotiation framing notes | — | Health-data compliance |
| Instinct | Values language | Priority empathy | Burnout-aware tone | Habit language |

---

## Runtime & skill

| Resource | Path |
|----------|------|
| Skill | `skills/saphira-weaver-everyday/SKILL.md` |
| Engine | `src/orchestration/weaver_everyday.py` |
| Core Weaver | `src/orchestration/weaver.py` |
| Tests | `tests/test_weaver_everyday.py` |

## Related

- [THE_WEAVER.md](./THE_WEAVER.md)
- [CREATIVE_COCREATION_CAPABILITIES.md](./CREATIVE_COCREATION_CAPABILITIES.md)
- [MULTIMODAL_CAPABILITIES.md](./MULTIMODAL_CAPABILITIES.md)
