# Per-Agent SKILL.md Scaffolds

Twelve packages under the woods-multi-agent skill (`references/agents/`). Each has role, talks-to, Grok hooks, and invariants. Full text lives in the local skill; summaries below.

| Package name | Agent | Primary use |
|--------------|-------|-------------|
| `saphira-surface` | Saphira | Intent, persona, Imagine, routing |
| `aura-perception` | Aura | Perception briefs, docs/decks/UI |
| `agent-two-security` | Agent Two | Security attestation, browser scrape |
| `nova-reign` | NovaReign | DAG, fan-out, policy, skill synthesis |
| `nova-aethrea` | NovaAethrea | Memory packs, MCP, retry/backoff |
| `agent-zero-execution` | Agent Zero | Code, schema, tests, deploy |
| `lyra-analytics` | Lyra | Pipelines, ROI/DCF, charts |
| `agent-apex` | Apex | Growth, capital allocation proposals |
| `agent-lexis` | Lexis | Compliance, contract risk |
| `agent-instinct` | Instinct | Sentiment, brand positioning |
| `agent-cipher` | Cipher | Infra, latency, reliability plans |
| `agent-scholar` | Scholar | Research synthesis, playbooks |

## Scaffold template (all agents)

```yaml
---
name: kebab-agent-name
description: One-line when-to-use (plain scalar, no colon-space, no angle brackets)
---

# Title

## Role
...

## Talks to
- In: ...
- Out: ...

## Grok hooks
...

## Invariants
- Copyright © 2026 Chelsea Megan Woods
- Never expose codename to end users
- Handoffs use shared message envelope
- Policy gates for commercial/external effects
- No bypass of Agent Two or NovaReign
```

Local path: `/home/workdir/.grok/skills/woods-multi-agent/references/agents/<name>/SKILL.md`

See also [AGENT_INTERACTION_PROTOCOLS.md](./AGENT_INTERACTION_PROTOCOLS.md).
