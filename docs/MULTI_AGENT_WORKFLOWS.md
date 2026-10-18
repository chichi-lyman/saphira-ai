# Multi-Agent Workflows

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai

Concrete implementation of the **Creation → Live Usage** multi-agent axis from [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md).

## What shipped

| Piece | Path |
|-------|------|
| DAG workflow engine | `src/orchestration/multi_agent_workflow.py` |
| Skill-backed workers | `src/orchestration/workers.py` |
| Platform HTTP API | `src/api/platform_router.py` → `/api/platform/workflows/*` |
| Entitlement metering | `src/platform/entitlements/metering.py` (`workflow_runs_per_day`) |
| Custom agent skills | `skills/saphira-code-reviewer/`, `saphira-systems-architect/`, `saphira-data-analyst/`, `saphira-security-auditor/` |
| Tests | `tests/test_multi_agent_workflow.py` |

## HTTP API (live platform)

Base: `/api/platform`

| Method | Path | Purpose |
|--------|------|--------|
| POST | `/workflows/run` | Generic runner (`template` + optional `custom_steps`) |
| POST | `/workflows/research-code-validate` | Research ‖ draft → code → validate |
| POST | `/workflows/analyze-architect-review` | Data ‖ arch ‖ review → synthesize |
| POST | `/workflows/secure-delivery` | Research ‖ arch → code → **security audit** → validate |
| GET | `/entitlements/{tenant_id}` | Plan, usage, remaining quotas |
| GET | `/entitlements/plans` | All plan limits including Super Saphira / Heavy |
| POST | `/entitlements/assign` | Assign plan to tenant |

Example:

```bash
curl -X POST /api/platform/workflows/secure-delivery \
  -H 'Content-Type: application/json' \
  -d '{"objective":"Ship webhook safely","tenant_id":"demo"}'
```

Quota exceeded → **HTTP 429** with metering detail.

## Templates

- `research_code_validate`
- `analyze_architect_review`
- `secure_delivery` (includes Security Auditor)
- `custom` — pass `custom_steps: [["name","capability"], ...]`

## Custom agent skills (sub-personas)

| Skill | Worker | Capabilities |
|-------|--------|--------------|
| Code Reviewer | `code_reviewer_agent` | code_review, development, quality |
| Systems Architect | `systems_architect_agent` | architecture, system, development |
| Data Analyst | `data_analyst_agent` | analytics, research, stem |
| **Security Auditor** | `security_auditor_agent` | security, quality, code_review |

Users only ever talk to **Saphira**; skills guide background workers.

## Super-tier metering

| Plan | workflow_runs / day | priority_compute |
|------|---------------------|------------------|
| free | 10 | no |
| pro | 50 | no |
| super_saphira | 200 | no |
| super_saphira_heavy | 1_000 | yes |
| enterprise | 5_000 | yes |

Enforced in `MultiAgentWorkflowEngine.run(..., tenant_id=...)` via `entitlements.enforce`.

## Related

- [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md)
- [SUPER_SAPHIRA_CAPABILITIES.md](./SUPER_SAPHIRA_CAPABILITIES.md)
- [AGENT_SKILL_FRAMEWORK.md](./AGENT_SKILL_FRAMEWORK.md)
- [AGENT_INTERACTION_PROTOCOLS.md](./AGENT_INTERACTION_PROTOCOLS.md)
