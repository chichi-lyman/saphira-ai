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

See `docs/AGENT_ALIGNMENT.md` and `docs/AGENT_SKILL_FRAMEWORK.md` in this repository.

| Domain agent | Category |
|--------------|----------|
| Agent Two | Browser and scraper |
| Agent Zero / Saphira | Full-stack engineering |
| NovaAethrea | MCP and integrations |
| Lyra | Data and finance |
| Aura | Docs, marketing, UI |
| NovaReign | Meta-orchestrator |
| Saphira (surface) | Primary assistant |

## Creating skills

1. Target repo and domain agent confirmed
2. Package as `skill-name/SKILL.md` + optional scripts/references/assets
3. Frontmatter: plain description scalar (no colon-space, no angle brackets)
4. Wire through capability registry — do not invent a second Saphira pipeline
5. Add tests under `tests/`

## References in-repo

- docs/AGENT_ALIGNMENT.md
- docs/AGENT_SKILL_FRAMEWORK.md
