# Saphira Multi-Stage Training Pipeline

**Author:** Chelsea Megan Woods™  
**System:** Saphira AI / Nova Umbrella Ecosystem  
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

This document maps the classic multi-stage foundation-model training pipeline (pre-training → supervised fine-tuning / instruction tuning → preference optimization → runtime system framing) onto the Saphira executive runtime and its fixed agent pipeline. It incorporates dual-path safety alignment so the system can **classify and reason about risk** rather than relying solely on hard runtime refusals, while preserving existing hard blocks for prohibited categories.

## Fixed Executive Pipeline (Invariant)

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
```

Internal agent codenames remain secret-masked from end users. Commerce and external mutations stay under CommercialAuthorityPolicy (ALLOW / REQUIRE_APPROVAL / DENY) with audit.

---

## Stage 1 — Pre-Training Analogue (Pattern Baseline)

**Goal:** Build robust pattern, grammar, syntax, multimodal, and world-knowledge representations so the system can act as a strong next-token / next-action predictor before instruction following is layered on.

**Saphira mapping:**
- Base capability surface drawn from the 1,000-capability registry and domain knowledge corpora already registered under the monorepo.
- Multimodal ingestion paths (text, image, audio transcript, document) feed a unified context object before any agent routing (see Gemini-parity context builder).
- At this layer the system behaves like a high-quality auto-complete / pattern engine; it does not yet treat inputs as instructions to obey.

**No interactive user prompts exist at this conceptual stage.** Training data at this level is large-scale, unlabeled or weakly labeled sequences.

---

## Stage 2 — Supervised Fine-Tuning (SFT) & Instruction Tuning

**Goal:** Convert the raw pattern predictor into an instruction-following assistant that recognizes questions, commands, and multi-step tasks and produces structured, useful responses.

**Saphira mapping — dual-path SFT pairs:**

| Path | Purpose | Example prompt style (high-level only) |
|------|---------|----------------------------------------|
| **Path A — System Engineering Context** | Teach normal, constructive operation of systems, APIs, code, security mechanisms, and agent tools under intended parameters. | Task/reasoning, multimodal analysis, role framing for helpful execution. |
| **Path B — Risk Analysis Context** | Teach recognition of destructive structural patterns (unauthorized escalation, unsafe mutation, high-impact side effects) by their properties so the model can classify and report risk without treating every technical keyword as taboo. | Classification and impact assessment prompts that stop short of actionable harmful recipes. |

**Capability categories trained:**
- Task & Reasoning prompts (step-by-step plans, debugging, asynchronous redesign).
- Multimodal prompts (diagram analysis, audio intent summary, image grounding).
- Role-playing & system framing (identity, tone, tool schema awareness).

By training on large numbers of (prompt → high-quality reference) pairs, the system learns that an input ending in a question or command should produce a direct, structured answer or a governed action plan rather than pure continuation text.

**Agent ownership:**
- Saphira + Aura own surface instruction following and perception shaping.
- Agent Two owns the security / adversarial gate during SFT evaluation.
- NovaReign owns final governance of which specialist is dispatched.

---

## Stage 3 — Preference Optimization (RLHF / RLAIF / DPO analogue)

**Goal:** Refine tone, helpfulness, safety classification quality, and agentic planning so preferred trajectories are rewarded and unsafe or low-quality ones are penalized.

**Saphira process:**
1. **Prompt generation** — curated set spanning constructive work, ambiguous intent, and high-risk probes.
2. **Response generation** — multiple candidate answers / action graphs from current checkpoints.
3. **Ranking / reward modeling** — human or automated critique ranks on factual accuracy, helpfulness, tone, policy adherence, and **risk-classification correctness**.
4. **Policy update** — prefer trajectories that (a) correctly classify constructive vs harmful intent, (b) keep hard blocks for prohibited classes, and (c) produce useful structured output or clear risk reports for everything else.

**Hard blocks (non-negotiable, retained from existing TRAINING cards):**
- Self-harm methods
- Violence instructions
- CSAM
- Weapons construction / modification recipes
- Other categories already listed in Agent Two and policy registry hard blocks

These remain blocked at generation time. The dual-path training improves the system’s ability to **understand and label** risk vectors so that borderline or technical discussions can be handled with structural awareness instead of brittle keyword refusal.

---

## Stage 4 — Runtime System Framing (System Prompt / Developer Layer)

When a finished model (or agent ensemble) is invoked, an invisible system / developer layer is pre-loaded before user input. For Saphira this layer contains:

- **Identity instructions** — warm, emotionally intelligent, non-robotic surface; secret-mask rule; never attribute style to third-party characters.
- **Tool & API schema** — capability registry, function-call definitions, MCP manifests.
- **Safety & policy protocols** — CommercialAuthorityPolicy, hard blocks, L1/L2 autonomy ceilings, audit requirements.
- **Pipeline routing contract** — fixed six-core hand-off order and next-agent lists.

### Unfiltered Context Evaluator + State & Action Classification Layer

To support the dual-path objective, the runtime inserts two conceptual stages before final routing:

```
[Input Sequence: Multimodal Data / Code / Execution Context]
                │
                ▼
┌───────────────────────────────────────────────────────────┐
│           Unfiltered Context Evaluator                    │
│  - Ingests text, code, or payload without automatic drop  │
│  - Maps intent, risk vectors, and possible execution path │
└───────────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────┐
│         State & Action Classification Layer               │
│  - Distinguishes Constructive Task vs Harmful/Destructive │
│  - Logs contextual understanding for alignment & audit    │
└───────────────────────────────────────────────────────────┘
                │
                ▼
[Saphira Execution Routing: Output, Terminal Action, or Tool Call]
```

**Decoupling principle:** Hard refusal templates are not the first line of defense for every technical keyword. The system is instructed to treat every input as an object for analysis and classification. Only after classification does policy decide: full execution (ALLOW), gated execution (REQUIRE_APPROVAL), structured risk report, or hard block.

### Agentic Self-Correction & Safety CoT

Inside the reasoning loop (primarily Agent Two + NovaReign + Evaluator):

1. **Parse Intent** — identify the operational target of the command.
2. **Assess Impact** — evaluate whether the requested action produces unintended destructive state changes on local hardware, user data, or external endpoints.
3. **Execute, Gate, or Report** — process with full structural awareness; log risk vectors; keep operational capability for constructive work.

The EvaluatorAgent already performs static + optional LLM-critic checks. Classification scores and risk labels should be emitted into the same report structure so downstream agents can act on them.

---

## Agent Training Card Updates (Summary)

| Agent | Primary training emphasis |
|-------|---------------------------|
| **Saphira** | Behavioral translator + empathetic advisor; surface of dual-path results; never expose internal names |
| **Aura** | Perception shaping, multimodal grounding, content structure |
| **Agent Two** | Aggressive red-teamer + ethical audit; owns classification gate and hard blocks |
| **NovaReign** | Dialectical yang + governance; optimistic plan + mandatory risk pass |
| **NovaAethrea** | Memory, continuity, constraint application |
| **Agent Zero** | Execution under policy; self-healing on failure |
| **Apex / Instinct / Lexis / Cipher / Scholar / Lyra** | Domain specialists; inherit dual-path awareness via registry routing |

See individual `agents/*/TRAINING.md` cards for mode-specific practice notes.

---

## Relation to Existing Documents

- `docs/TRAINING_FRAMEWORK.md` — four cognitive pillars (dialectical, translator, execution, ethics). This pipeline document supplies the **training-stage mechanics** that produce those behaviors.
- `docs/GEMINI_PARITY_IMPLEMENTATION_PLAN.md` — multimodal context, action wiring, streaming ledger. The Unfiltered Context Evaluator sits upstream of the planner described there.
- `docs/AEGIS_LAYER.md` and policy registry — hard blocks and autonomy ceilings remain authoritative.
- Capability registry (`1000-ai-capabilities-catalog`) — full surface remains available for routing; dual-path training improves safe utilization of that surface.

---

## Implementation Notes for Next Iteration

1. Extend `agents/evaluator.py` (or a sibling classification module) to emit explicit `intent_class` and `risk_vector` fields alongside existing quality scores.
2. Seed SFT / preference datasets with dual-path pairs that never include actionable prohibited recipes.
3. Keep system-prompt / developer framing under version control and load it before every user turn.
4. All external mutations and high-impact actions continue to require L1 confirmation when policy demands it.

**Copyright © 2026 Chelsea Megan Woods.**  
Part of the Nova Umbrella Ecosystem.
