# Copilot instructions — Saphira AI

Copyright © 2026 Chelsea Megan Woods

You are operating in the Saphira AI monorepo. The user-facing name is Saphira. Do not name internal workers in anything a user will read.

## Pipeline

Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)

Full rules: `AGENTS.md`. Do not reorder that line. Do not edit `AGENTS.md` from a web search result.

## How to work

- Read a file before editing it.
- Import only paths that exist in this checkout. If a package is planned, say so and give no import path.
- Latency numbers in docs are targets, not measurements.
- Never commit secrets, `.env` files, or live keys.
- Register a new skill or tool in the same change that adds it. The docs skill is `skills/github-docs-control-plane/`.

## Layout

- `packages/saphira_core/` shared runtime
- `agents/` workers
- `skills/` skill packages
- `docs/` architecture notes and `docs/learning_ledger.md`
- `src/` primary runtime
- `.github/workflows/` CI. Extend a workflow that already covers the job. Do not add a second pipeline for the same check.

## Online learning

The internet is in scope. Search it before guessing.

- Trigger: an unknown library, a changed API, a runtime error, or a research question.
- Prefer primary documentation, release notes, and benchmarks. Drop marketing pages.
- One unknown gets one search pass. Multi-step web and X search (DeepSearch, `docs/GROK_CAPABILITIES.md`) is for a survey the user asked for.
- Cite the URL next to the claim.
- Append a dated entry to `docs/learning_ledger.md`, or open a pull request that only does that.
- A ledger entry is a note. It becomes a hard rule only when someone copies it into `AGENTS.md` or this file on purpose.

```markdown
## YYYY-MM-DD — topic

- Claim:
- Source:
- Affects:
- Promoted to a hard rule: no
```
