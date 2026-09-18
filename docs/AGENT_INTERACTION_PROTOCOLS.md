# Agent Interaction Protocols (Nova Umbrella)

All handoffs are mediated. End users never see internal codenames. Commercial side effects require policy gates.

## Shared message envelope

```json
{
  "trace_id": "...",
  "from_agent": "nova_reign",
  "to_agent": "agent_zero",
  "task_id": "...",
  "objective": "...",
  "constraints": [],
  "inputs": {},
  "policy": "ALLOW | REQUIRE_APPROVAL | DENY",
  "deadline_ms": null,
  "reply_channel": "orchestrator"
}
```

Status values: `ACCEPTED`, `IN_PROGRESS`, `NEED_INPUT`, `NEED_APPROVAL`, `COMPLETED`, `FAILED`, `ESCALATED`.

## Pipeline handoff protocol (immutable order)

```
Saphira → Aura → Agent Two → NovaReign → NovaAethrea → Agent Zero
```

| From | To | When | Payload focus | Failure behavior |
|------|-----|------|---------------|------------------|
| Saphira | Aura | User intent parsed | Goal, modality, user context | Soft retry; clarify with user if ambiguous |
| Aura | Agent Two | Perception ready | Scene, media, risk signals | If perception fails, Saphira reports limited awareness |
| Agent Two | NovaReign | Security scan done | Threat status, allowed tools | RED → quarantine path; no execution |
| NovaReign | NovaAethrea | Plan approved | Plan DAG, memory queries | If governance DENY, stop and notify Saphira |
| NovaAethrea | Agent Zero | Memory + tools bound | Context pack, tool grants | Missing memory → partial context flag |
| Agent Zero | NovaReign | Work finished | Artifacts, logs, metrics | On failure, NovaReign may replan or escalate |

NovaReign may **fan-out** to extended specialists (Apex, Lexis, Instinct, Cipher, Scholar, Lyra) in parallel, then **fan-in** before authorizing Agent Zero.

## Per-agent rules (summary)

| Agent | Inbound | Outbound | Hard rule |
|-------|---------|----------|-----------|
| **Saphira** | User input, summarized results | User-safe language only | Never reveal codenames |
| **Aura** | Intent, media | Perception briefs; content artifacts | Perception before security advances |
| **Agent Two** | Perception, browse tasks | GREEN/RED; scrape JSON | RED blocks execution |
| **NovaReign** | Attested intents, specialist outputs | DAG plans, policy decisions | Sole release authority for Agent Zero |
| **NovaAethrea** | Memory/MCP grants | Context packs, connector health | No MCP without grant |
| **Agent Zero** | Sealed packages only | Artifacts, test reports | Refuse unsigned packages |
| **Lyra** | Metric tasks | Models, charts | Spend-impact needs approval |
| **Apex** | Growth objectives | Revenue/allocation proposals | Cannot move funds |
| **Lexis** | Contracts, workflows | Risk briefs; veto recommend | Legal RED → governance stop |
| **Instinct** | Brand goals, signals | Sentiment, positioning | Budget campaigns need approval |
| **Cipher** | Telemetry, arch requests | Refactor/reliability plans | Apply via Agent Zero + CI |
| **Scholar** | Research questions | Playbooks, modules | Publish needs governance |

## Escalation ladder

1. Agent-local retry (bounded)
2. NovaReign replan / alternate specialist
3. REQUIRE_APPROVAL → human
4. DENY → Saphira informs user safely

## Parallelism

Example: Apex + Instinct + Lyra on growth; Lexis + Cipher on release. Fan-in barrier before Agent Zero.

## Related

- [AGENT_ALIGNMENT.md](./AGENT_ALIGNMENT.md)
- [ORCHESTRATION_FRAMEWORKS.md](./ORCHESTRATION_FRAMEWORKS.md)
- [AGENT_SKILL_SCAFFOLDS.md](./AGENT_SKILL_SCAFFOLDS.md)
