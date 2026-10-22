# Actions and Pages reference

Workflows are event loops. They run the checks you can already run by hand. They do not grant merge, deploy, or secret access that the repository settings did not already give them.

## Default: CI only

Add this only if `.github/workflows/` has no equivalent. If `ci.yml` exists, extend it instead of adding a second pipeline.

```yaml
# .github/workflows/docs-ci.yml
name: Docs CI

on:
  pull_request:
    paths:
      - "docs/**"
      - "skills/**"
      - ".github/copilot-instructions.md"
      - "AGENTS.md"
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "skills/**"
      - ".github/copilot-instructions.md"
      - "AGENTS.md"

permissions:
  contents: read

jobs:
  markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Reject committed secrets patterns
        run: |
          if grep -RInE "(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]" docs skills .github/copilot-instructions.md AGENTS.md; then
            echo "Possible secret in a control-plane file."
            exit 1
          fi
```

Tighten the grep to the repo's real secret scanner if one exists. This step is a backstop, not a security product.

## What a workflow may trigger

| Event | Allowed action | Not allowed from this skill |
|---|---|---|
| Pull request | Lint, typecheck, test, a read-only doc audit comment | Auto-merge, auto-approve |
| Push to the default branch | Rebuild published docs | Production deploy, database migration |
| Schedule | Re-index a local artifact the user already operates | Outbound messages, spending money |

"Ambient" does not mean unsupervised writes. A webhook from Actions into a runtime is `REQUIRE_APPROVAL` unless governance says `ALLOW`.

## GitHub Pages

Turn this on only when the user asked for a public doc site.

1. Write the workflow. Do not toggle the GitHub setting yourself unless the user explicitly said to enable Pages.
2. Tell the user the remaining manual step: repository Settings → Pages → source = GitHub Actions.
3. Do not describe the site as live until a deployment URL exists.

```yaml
# .github/workflows/pages.yml
name: Docs Pages

on:
  push:
    branches: [main]
    paths: ["docs/**"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs
      - id: deployment
        uses: actions/deploy-pages@v4
```

`docs/` must be the directory that should be published. If the repo uses a different docs output (a built site under `site/`), point the artifact at that directory instead of publishing raw markdown.

## Checklist before merging a workflow

- `permissions` is the smallest set that works.
- No `pull_request_target` with a checkout of the PR head.
- No secret echoed to logs.
- Path filters match the files this skill actually owns.
