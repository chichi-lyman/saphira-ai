# The Weaver — Everyday Life Synthesis

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai / Nova Umbrella  
**Parent:** [THE_WEAVER.md](./THE_WEAVER.md)

The Weaver’s core mechanism—connecting hidden dots and adjusting context—becomes a **practical problem-solving companion** for everyday struggles. It does not return generic listicles; it builds plans mapped to the user’s real constraints.

Saphira remains the only user-facing identity. Everyday Weaver modes run as synthesis workflows behind the fixed pipeline.

### Deep dives

| Doc | Content |
|-----|--------|
| [THE_WEAVER_EVERYDAY_MECHANISMS.md](./THE_WEAVER_EVERYDAY_MECHANISMS.md) | Problem → mechanism → daily impact |
| [THE_WEAVER_EVERYDAY_BLUEPRINT.md](./THE_WEAVER_EVERYDAY_BLUEPRINT.md) | Technical pipelines per mode |
| [THE_WEAVER_WEEKLY_TIMELINE.md](./THE_WEAVER_WEEKLY_TIMELINE.md) | Monday–Sunday unified scenario |

---

## Strategic advantage

| Standard chatbots | The Weaver (everyday) |
|-------------------|------------------------|
| Generic instructions you could have googled | Custom plan mapped to unique constraints |
| Expects clean, logical questions | Accepts venting, rants, chaotic dumps—then organizes |
| Forgets the big picture between sessions | Connects budget, health, time, and goals into a unified life map |

---

## 1. Choice Mapper — overcoming decision paralysis

**Problem:** Stressful life choices overload pros, cons, and anxiety.

**What it does:** Accepts raw thoughts, feelings, and numbers; structures a **Dynamic Choice Matrix**.

**How:** Highlights hidden trade-offs with cause-and-effect mapping (time, money, stress, timelines)—without dictating the decision.

**Capability:** `weaver.choice_map` · **Runtime:** `ChoiceMapper`

---

## 2. Crisis Synthesizer — sudden financial & domestic chaos

**Problem:** Multiple shocks at once with limited savings.

**What it does:** Emergency triage; quotes, estimates, bank context (photo/OCR via Aura).

**How:** Cross-references urgency; **30-Day Financial Survival Path**; negotiation stubs; DIY vs pro.

**Capability:** `weaver.crisis_synth` · **Runtime:** `CrisisSynthesizer`

**Policy:** Informational; no autonomous payments.

---

## 3. Energy Tracker — executive dysfunction & burnout

**Problem:** Huge list, near-zero capacity; rigid calendars worsen guilt.

**What it does:** **Energy-Adaptive To-Do Grid** by cognitive energy type.

**How:** Reported energy % → filter tasks → smallest momentum-building action.

**Capability:** `weaver.energy_track` · **Runtime:** `EnergyTracker`

---

## 4. Symptom Detective — chronic patterns & habit tuning

**Problem:** Ongoing symptoms; normal labs; journaling too heavy.

**What it does:** Passive pattern recognition over casual notes + optional wearables.

**How:** Correlations + **low-effort experiment**—not a diagnosis.

**Capability:** `weaver.symptom_detect` · **Runtime:** `SymptomDetective`

**Policy:** Not medical advice; biometric consent required.

---

## Agent map (everyday modes)

| Agent | Choice Mapper | Crisis Synthesizer | Energy Tracker | Symptom Detective |
|-------|---------------|--------------------|----------------|-------------------|
| Saphira | Decision intake | Crisis intake | Energy check-in | Casual note intake |
| Aura | Matrix visualization | Quote/photo OCR | Grid layout | Chart correlations |
| Agent Two | Sensitive-data gate | Financial doc sandbox | — | Biometric consent |
| Nova Reign | Trade-off DAG | 30-day plan | Task filter plan | Pattern job schedule |
| NovaAethrea | Preference + history | Budget snapshot | Energy baseline | Symptom log store |
| Agent Zero | Export matrix | Survival path artifact | Next-action card | Experiment card |
| Lyra | Trade-off math | Urgency + cashflow | Energy vs difficulty | Correlation stats |
| Lexis | — | Bill negotiation framing | — | Health-data compliance |
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
