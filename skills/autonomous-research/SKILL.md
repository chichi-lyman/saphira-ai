---
name: autonomous-research
description: Bounded autonomous web research worker under Nova Reign and Agent Two. Creates task contracts, runs allow-listed scraping with strict budgets, produces schema-validated evidence, and writes provenance to NovaAethrea. Never performs form submission, login, purchase, or messaging without elevated approval. Use for scheduled competitor monitoring, market scans, public-source synthesis, and on-demand research goals.
---

# Autonomous Research Capability

## Purpose

Give Saphira and the Nova Umbrella an independent research brain that can scrape and synthesize public internet sources on its own schedule while remaining fully governed, auditable, and privacy-preserving.

## Ownership & Placement

- **Governance**: Nova Reign (creates and owns the Task Contract)
- **Execution surface**: Agent Two (browser / security)
- **Memory & evidence**: NovaAethrea
- **Pipeline position**: after security stage, before final execution stage
- **Never bypasses**: CommercialAuthorityPolicy, domain allow-list, or action budget

## When to use

- User requests ongoing monitoring of public sites
- Scheduled research jobs (daily/weekly competitor or market scans)
- Multi-source public synthesis that exceeds a single search call
- Any research goal that benefits from iterative navigation + extraction

## When NOT to use

- Personal inbox, calendar, or private account data (privacy-first rule)
- Any action that changes external state (post, buy, message, create account)
- Unbounded open-web crawling without a domain allow-list
- Continuous ambient background surveillance

## Task Contract

Every run begins with a validated `AutonomousResearchTaskContract`.

Required fields:
- `goal`
- `success_criteria`
- `allowed_domains`
- `action_budget` (max_pages, max_seconds, max_cost_usd)
- `output_schema`
- `approval_level`

## Worker Lifecycle

1. Nova Reign creates and validates the contract.
2. Agent Two `start(contract)` → returns `run_id`.
3. Worker executes the observe → decide → act → evaluate loop.
4. Steps and evidence stream to NovaAethrea.
5. Final `WorkerResult` is returned; contract is closed.

## Hard Limits (enforced in code)

- Domain allow-list is absolute.
- Default prohibited actions: `form_submit`, `login`, `purchase`, `message`, `create_account`.
- Budget exhaustion or policy denial immediately stops the worker.
- All extracted records must pass deterministic schema validation.

## Output

- Structured evidence records with provenance
- Step-by-step execution ledger
- Final summary (optional)
- Full audit trail for governance review

## Integration Notes

- Register this skill in the Capability Registry under domain “Multi-Agent Systems & Autonomous Operations” and “Security, Privacy…”.
- Surface results to the user through Saphira’s normal persona (never expose internal agent names).
- For interactive browser use, prefer the existing Chrome Extension Auto Browse path with dry-run preview.
- Scheduled runs are created by Nova Reign; the worker itself has no persistent scheduler.

## References

- `references/task-contract-schema.json`
- `references/worker-interface.py`
- Agent Two browser tooling (Playwright preferred)
- Privacy-first pillars (on-demand only, no ambient personal data)
- CommercialAuthorityPolicy gates
