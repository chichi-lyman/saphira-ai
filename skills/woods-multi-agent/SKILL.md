---
name: woods-multi-agent
description: Build and extend multi-agent systems for Chelsea Megan Woods projects under chichi-lyman GitHub including Saphira AI, Nova Umbrella, Woods Legacies, and related assistants. Use when creating sub-agents, SKILL.md bundles, browser automation, full-stack agent skills, MCP connectors, analytics agents, document generators, or hierarchical orchestrators for any chichi-lyman repository.
---

# Woods Multi-Agent Skill Framework

Specialize work for the **chichi-lyman** GitHub ecosystem. Preserve Saphira pipeline and persona invariants.

## Core invariants

- Copyright © 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
- Pipeline: Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
- Never expose internal agent codenames to end users
- Policy-gated commerce (ALLOW / REQUIRE_APPROVAL / DENY)
- No secrets in git

## Agent alignment

See `docs/AGENT_ALIGNMENT.md`.

**Core pipeline:** Saphira, Aura, Agent Two, NovaReign, NovaAethrea, Agent Zero, Lyra

**Extended family:**

| Agent | Identity |
|-------|----------|
| Agent Apex | Venture Strategist — revenue, capital, growth |
| Agent Lexis | Regulatory Guardian — compliance, contracts, risk |
| Agent Instinct | Market and Consumer Whisperer — sentiment, trends, brand |
| Agent Cipher | System Architect and Optimizer — infrastructure, reliability |
| Agent Scholar | Rapid Knowledge Synthesizer — research, playbooks, training |

Specialists dispatch via NovaReign or the capability registry. Never bypass security or governance.

## Grok built-in capabilities

Prefer Grok natives. See `docs/GROK_CAPABILITIES.md`.

| Capability | Domain fit |
|------------|------------|
| DeepSearch and real-time synthesis | Agent Two, Lyra, Instinct |
| Extended reasoning | Saphira, NovaReign, Scholar |
| Grok Imagine | Saphira Imagine, Aura |
| Code execution and debugging | Agent Zero, Cipher |
| Agentic tool calling | NovaAethrea, capability registry |

## Creating skills

1. Target repo and domain agent confirmed
2. Package as `skill-name/SKILL.md` + optional scripts/references/assets
3. Declare which Grok capability is used; only ship project-specific scripts and policy
4. Frontmatter: plain description scalar (no colon-space, no angle brackets)
5. Wire through capability registry — do not invent a second Saphira pipeline
6. Add tests under `tests/`

## References in-repo

- docs/AGENT_ALIGNMENT.md
- docs/AGENT_SKILL_FRAMEWORK.md
- docs/GROK_CAPABILITIES.md
