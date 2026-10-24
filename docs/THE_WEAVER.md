# The Weaver — Contextual Cartographer & Synthesis Engine

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai / Nova Umbrella  
**Nickname:** The Weaver

Unlike turn-by-turn chatbots or flat search engines, The Weaver **maps, visually structures, and bridges gaps between disparate human ideas in real time**. Saphira remains the only user-facing identity; The Weaver operates as a specialized synthesis mode behind the fixed executive pipeline.

**Everyday life modes** (Choice Mapper, Crisis Synthesizer, Energy Tracker, Symptom Detective) are documented in [THE_WEAVER_EVERYDAY.md](./THE_WEAVER_EVERYDAY.md).

---

## What it does

### Dynamic Concept Mapping
As the user speaks or types a messy brainstorm, The Weaver charts thoughts as a multi-dimensional visual graph. Nodes link to historical precedents, scientific formulas, or artistic movements the user may not have named.

### Cross-Disciplinary Synthesizing
Given concepts from distant domains (e.g. botany + Renaissance architecture), it searches for **structural analogies** (cell walls ↔ gothic vaults) and proposes novel frameworks.

### Intuitive Level-Shifting
A conceptual slider changes the entire output frame:

| Position | Mode | Output style |
|----------|------|--------------|
| Left | Explain to an 8-year-old | Conceptual analogies, plain language |
| Center | General synthesis | Balanced maps and bridges |
| Right | Post-doctoral technical review | Citations, proofs, formal structure |
| Up | Sci-fi avant-garde | Surrealist fiction prompts, speculative leaps |

---

## How it operates (three-tier loop)

```
[User Input: Raw Brainstorm]
          │
          ▼
┌─────────────────────────────────────────┐
│  1. GRAPH-GROUNDED PARSING              │  semantic nodes & intents
└─────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  2. HYBRID VECTOR & VECTOR-GRAPH RAG    │  cross-discipline retrieval
└─────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  3. DYNAMIC INTERACTIVE VISUALIZATION   │  interactive concept maps
└─────────────────────────────────────────┘
```

1. **Graph-Grounded Parsing** — Break input into semantic nodes (entities, emotions, rules) and map onto a curated knowledge graph—not only token probabilities.
2. **Hybrid Vector & Topological RAG** — Combine vector embeddings with network topology to find data points that are **maximally distant but mathematically analogous** (the creative sweet spot).
3. **Real-Time Vector UI Generation** — Render responsive canvas layouts (timeline, simulation, logic branch) that morph to the data type.

---

## Why this design

Humanity has abundant fragmented information and scarce synthesis. Search returns raw lists; average chat returns statistical text. Historic leaps often happen at **bridges between silos** (biology + engineering → biomimicry). The Weaver is a **cognitive mirror**: it organizes imaginative noise, highlights hidden connections, and supplies structure so a “crazy idea” can become a plan—without doing the user’s thinking for them.

---

## Agent placement

| Agent | Weaver role |
|-------|-------------|
| **Saphira** | Intake brainstorm; present maps in warm language; level-shift UX |
| **Aura** | Visual graph layout, canvas morph, perception of uploaded sketches |
| **Agent Two** | Gate unsafe analogy domains; sandbox external graph queries |
| **Nova Reign** | Plan parse → RAG → visualize DAG; fan-out cross-domain workers |
| **NovaAethrea** | Persist concept graphs, user map history, embedding packs |
| **Agent Zero** | Render/export graph artifacts (JSON, SVG, interactive HTML) |
| **Lyra** | Analogy strength metrics, distance scores, graph statistics |
| **Apex** | Package synthesis frameworks as productizable IP (policy-gated) |
| **Lexis** | Citation integrity, training-data and IP notes on analogies |
| **Instinct** | Audience-level language for level-shift modes |
| **Cipher** | Graph render latency, local canvas performance |
| **Scholar** | Cross-domain literature bridges and precedent briefs |

---

## Runtime anchors

| Resource | Path |
|----------|------|
| Skill (core) | `skills/saphira-weaver/SKILL.md` |
| Skill (everyday) | `skills/saphira-weaver-everyday/SKILL.md` |
| Engine (core) | `src/orchestration/weaver.py` |
| Engine (everyday) | `src/orchestration/weaver_everyday.py` |
| Everyday doc | [THE_WEAVER_EVERYDAY.md](./THE_WEAVER_EVERYDAY.md) |

## Policy

- Never present internal agent names in Weaver outputs.
- Analogies must be labeled as proposed bridges, not proven facts, unless grounded.
- Everyday finance/health modes are informational only—not professional advice.
- Commercial packaging of synthesis IP stays under ALLOW / REQUIRE_APPROVAL / DENY.

## Related

- [THE_WEAVER_EVERYDAY.md](./THE_WEAVER_EVERYDAY.md)
- [CREATIVE_COCREATION_CAPABILITIES.md](./CREATIVE_COCREATION_CAPABILITIES.md)
- [MULTI_AGENT_WORKFLOWS.md](./MULTI_AGENT_WORKFLOWS.md)
- [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md)
