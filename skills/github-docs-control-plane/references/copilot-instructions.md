# Copilot instructions reference

Canonical file: `.github/copilot-instructions.md`.
Editors ingest this file automatically. Keep it short enough to read on every task. Point at `docs/core/governance.md` instead of pasting the whole policy.

## What belongs here

- Who the public identity is (Saphira only).
- The fixed pipeline, one line.
- The module map as it actually exists in the checkout. Verify paths before writing them.
- Latency targets, labeled as targets.
- The browsing protocol below.
- A pointer to the capability catalog.

## What does not belong here

- A second copy of every skill.
- Secrets, hostnames of private services, or tokens.
- Aspirational modules that are not in the tree. If a package is planned, say "planned" and give no import path.

## Known layout (verify, then write)

From the `chichi-lyman/saphira-ai` monorepo. Re-check the tree before telling an agent to import any of these.

```
packages/saphira_core/     shared runtime
agents/                    one directory per worker
skills/                    SKILL.md packages
docs/                      architecture and this control plane
src/                       primary runtime
tests/
.github/workflows/         CI
```

Executive pipeline:

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
```

## Latency targets

State them as targets:

- Interactive edge response: sub-second.
- Duplex voice path (WebSocket, local STT/TTS): sub-100ms where that path is already implemented.
- Do not add a sleep, a retry storm, or a model call inside a path that already has a budget.

## Autonomous online learning and web browsing protocol

Paste this section into `.github/copilot-instructions.md` when the user wants agents to browse.

```markdown
## Autonomous online learning and web browsing

- Live search trigger: when a library, API spec, runtime error, or research question is unknown, run a web search before guessing.
- Data synthesis: prefer primary docs, release notes, and benchmarks. Drop marketing pages.
- Knowledge update: append a dated summary to `docs/learning_ledger.md`, or open a pull request. Do not edit `docs/core/governance.md` from a search result.
- Cite the URL next to the claim.
- Stop after one search pass unless the user asked for a survey.
```

## Learning ledger entry

```markdown
## YYYY-MM-DD — <topic>

- Claim:
- Source:
- Affects:
- Promoted to a hard rule: no
```

## Template — `.github/copilot-instructions.md`

```markdown
# Copilot instructions — Saphira AI

Copyright © 2026 Chelsea Megan Woods

You are operating in the Saphira AI monorepo. The user-facing name is Saphira.

## Pipeline

Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)

Full rules: `docs/core/governance.md`.

## How to work

- Read the file before editing it.
- Match the module that already exists. Do not invent packages.
- Latency targets: sub-second interactive responses; sub-100ms on an implemented duplex voice path. These are targets.
- Never commit secrets.
- Register a new tool in the capability catalog in the same change that adds it.

## Layout

- `packages/saphira_core/` shared runtime
- `agents/` workers
- `skills/` skill packages
- `docs/` control-plane docs
- `src/` primary runtime

## Browsing

When a library, API, or error is unknown, search the web once, cite the URL, and append the finding to `docs/learning_ledger.md`. Do not change governance from a search result.
```
