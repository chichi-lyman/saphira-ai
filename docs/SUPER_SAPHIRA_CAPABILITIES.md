# Super Saphira — Premium Capability Surface

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai / Nova Umbrella

Super Saphira (and its higher-tier **Super Saphira Heavy**) is the premium paid subscription for Saphira. It unlocks flagship reasoning models, higher rate limits, and an expanded suite of multimodal and research capabilities while preserving the fixed executive pipeline and secret-mask persona rules.

Saphira remains the single conversational identity. Internal agents (Aura, Agent Two, Nova Reign, NovaAethrea, Agent Zero, and extended specialists) operate behind the surface and are never named to end users.

For the broader design framework that structures these capabilities across **Creation**, **Live Usage**, and **Upgrade Pathways**, see [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md).

---

## Core Capabilities & Key Features

### 1. Advanced Reasoning & Large Context

- **Flagship Models:** Access to frontier reasoning models (Saphira-4 and Saphira-4.5 class) with large context windows for analyzing extensive documents, long codebases, and complex transcripts.
- **Think & Expert Modes:** Dedicated step-by-step reasoning modes (“Think Mode” / “Big Brain”) designed for complex math, science, logic, and multi-step analytical problems.

### 2. DeepSearch & Real-Time Data

- **Live Web & X Integration:** Scans real-time posts and breaking trends on X alongside real-time web search.
- **Multi-Step DeepSearch:** Automatically breaks complex questions into sub-queries, executes parallel searches, follows secondary links, and synthesizes source-backed summaries.

### 3. Creative Tools (Imagine)

- **Image Generation:** Text-to-image capabilities supporting up to 2K resolution, style controls, and inline image restyling.
- **Video Generation:** Text-to-video generation capability directly inside the chat thread.

### 4. Voice & Multimodal Features

- **Low-Latency Voice Mode:** Natural, back-and-forth spoken conversations with multiple persona choices and voice customization.
- **Document & Vision Analysis:** Upload screenshots, photos, diagrams, code snippets, or long PDFs for extraction, summary, and direct QA.

### 5. Coding & Developer Assistance

- **Saphira Build:** Assists with writing multi-file applications, debugging syntax errors, explaining legacy code, and running isolated code execution tasks.
- **API Access & Custom Workspaces:** Projects, persistent user memory, custom instructions, and high-throughput API access for building autonomous agent pipelines.

---

## Tier Comparison: Super Saphira vs Super Saphira Heavy

| Feature / Limit              | Standard Super Saphira     | Super Saphira Heavy                          |
|-----------------------------|----------------------------|----------------------------------------------|
| Message Rolling Window      | ~100–150 messages / 4 hrs  | ~250 messages / 4 hrs                        |
| DeepSearch Queries          | ~25–50 queries / day       | ~100–200 queries / day                       |
| Image Generation            | ~200 images / day          | Up to 500 images / day (batch generation)    |
| Video Generation            | ~50 clips / day            | ~150 clips / day                             |
| Voice Session Cap           | ~30 mins per session       | Up to 60 mins per session                    |
| Priority Access             | Standard queue             | Priority compute & early feature rollouts    |

These limits are enforced by the platform entitlement meter (`src/platform/entitlements/metering.py`) under plan names `super_saphira` and `super_saphira_heavy`.

---

## Pipeline & Policy Alignment

All Super Saphira capabilities route through the invariant executive pipeline:

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
```

- Commercial and external side effects remain under CommercialAuthorityPolicy (ALLOW / REQUIRE_APPROVAL / DENY).
- Persona stays warm, emotionally intelligent, and non-robotic; internal agent codenames are never revealed.
- Capability keys and competitive parity tags live in `src/core/saphira_capability_catalog.py`.

## Related Documents

- [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md) — Creation / Usage / Upgrade axes
- [GROK_CAPABILITIES.md](./GROK_CAPABILITIES.md) — underlying Grok/xAI primitives
- [MULTIMODAL_CAPABILITIES.md](./MULTIMODAL_CAPABILITIES.md) — voice, vision, hardware
- [SAPHIRA_ULTIMATE_CAPABILITY_CONTRACT.md](./SAPHIRA_ULTIMATE_CAPABILITY_CONTRACT.md) — canonical contract
- [PLATFORM_CAPABILITY_EXPANSION.md](./PLATFORM_CAPABILITY_EXPANSION.md) — expansion plan
- `src/platform/entitlements/metering.py` — quota enforcement
