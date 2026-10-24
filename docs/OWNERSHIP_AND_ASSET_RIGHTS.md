# Ownership & Asset Rights Verification

**Owner:** Chelsea Megan Woods  
**Entities:** Woods AI Studio / Lyman Legacies / Nova Umbrella / Chelsea Woods & Co.  
**Last verified:** 2026-10-19

---

## Current Status

| Item | Status | Notes |
|------|--------|-------|
| Root `LICENSE` | Present & strong | Proprietary, explicit All Rights Reserved, contact path |
| `pyproject.toml` license field | Present | "Proprietary © 2026 Chelsea Megan Woods" |
| Core runtime files (`src/core/`, `src/agents/`) | Mostly consistent | Standard header present on primary modules |
| Package stubs under `agents/*/` | Partial | Some minimal headers; being standardized |
| Skills under `skills/` | Good | New skills include full copyright block |
| Frontend (`saphira-app/`) | Needs sweep | Verify all source files carry header |

## Canonical Header (use on all new/updated source files)

```text
# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
```

For Markdown / docs:
```text
**Copyright © 2026 Chelsea Megan Woods**  
All rights reserved under Woods AI Studio / Lyman Legacies / Nova Umbrella.
```

## Verification Checklist (for due diligence / exit readiness)

- [x] Root LICENSE is proprietary and names Chelsea Megan Woods exclusively
- [x] pyproject.toml declares proprietary ownership
- [ ] All Python modules under `src/` and `agents/` carry the canonical header
- [ ] Frontend TypeScript/TSX files carry equivalent notice
- [ ] No third-party code is present without clear license compatibility notes
- [ ] No contributor agreements or external PRs that could cloud ownership
- [ ] Secrets and API keys never committed (env-only)
- [ ] Trademark / brand references (Saphira™, Nova Umbrella™) are consistent

## Action Items in Progress

1. Standardize remaining minimal headers in `agents/*/agent.py` stubs.
2. Add a simple pre-commit or CI check that fails if a new `.py` file lacks the copyright line.
3. Produce a one-page "Clean Ownership Certificate" PDF for buyer data rooms when needed.

**Copyright © 2026 Chelsea Megan Woods**
