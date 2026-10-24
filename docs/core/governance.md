# Core governance

Copyright © 2026 Chelsea Megan Woods  
Parent system: Saphira AI / Nova Umbrella

## Pipeline

Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)

Do not reorder. Do not add a parallel executive path.

## Public speech

User-facing text uses the name Saphira only. Internal workers stay unnamed in anything a user will read.

## Worker responsibilities

| Worker | Owns | Does not own |
|---|---|---|
| Saphira | Intent, user-facing replies, task intake | Direct production writes |
| Aura | Perception: files, screens, logs, retrieved context | Decisions that change policy |
| Agent Two | Security review, secret scanning, input validation | Feature design |
| Nova Reign | Governance: does this change violate a written rule? | Implementation |
| NovaAethrea | Memory, catalogs, MCP registration, learning ledger | Ungated side effects |
| Agent Zero | Execution: edits, tests, commits the user asked for | Merging to the protected branch |

Extended specialists do not sit on the executive path.

## Boundaries

- No secrets, `.env` files, or live API keys in the repo.
- No edits to production route handlers from a documentation or example task.
- External side effects default to `REQUIRE_APPROVAL` unless this file explicitly says `ALLOW`.
- Latency figures elsewhere are targets, not measurements (sub-second interactive edge; sub-100ms duplex voice where the path already exists).
- No destructive automation (auto-merge, force-push, production deploy) from a markdown change alone.
- A governance change lands as its own pull request; it does not ride with an unrelated feature.

## Change control

Policy classes for side effects: `ALLOW`, `REQUIRE_APPROVAL`, `DENY`.
