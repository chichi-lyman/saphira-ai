# Saphira AI — Monorepo

© 2026 Chelsea Megan Woods

Unified workspace for **Saphira AI** and all specialist agents under one repository.

## Layout

```text
saphira-ai/
├── pyproject.toml          # Root project + workspace members
├── requirements.txt        # Runtime deps (unified)
├── requirements-dev.txt    # Dev/test/lint
├── Makefile                # Common build targets
├── .python-version
├── packages/
│   └── saphira_core/       # Shared runtime (orchestration, connectors, growth)
├── agents/                 # All agents (one directory each)
│   ├── saphira/
│   ├── aura/
│   ├── agent_two/
│   ├── novareign/
│   ├── novaaethrea/
│   ├── agent_zero/
│   ├── lyra/
│   ├── apex/
│   ├── instinct/
│   ├── lexis/
│   ├── cipher/
│   └── scholar/
├── src/                    # Legacy / primary runtime entry (compat)
├── tests/
└── .github/workflows/
    ├── ci.yml              # Unified pipeline
    └── test.yml            # Compat alias
```

Standalone repos (`agent-apex`, `agent-instinct`, …) remain on GitHub as identity mirrors; **this monorepo is the build and dependency source of truth**.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip uv
uv pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
make test
```

Or with uv only:

```bash
uv sync
uv run pytest
```

## Secrets (growth / social)

`OPENAI_API_KEY` · `FEEDHIVE_TRIGGER_URL` · `PUBLER_API_TOKEN`
