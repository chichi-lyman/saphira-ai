# Saphira AI — Monorepo

© 2026 Chelsea Megan Woods

Unified workspace for **Saphira AI** and all specialist agents under one repository.

Saphira is the only user-facing identity. Internal agents (Aura, Agent Two, Nova Reign, NovaAethrea, Agent Zero, Lyra, and extended specialists) stay secret-masked behind the fixed executive pipeline.

## Publications & Technical Evaluation Frameworks

Technical writing, multi-agent evaluation rubrics, SFT/RLHF-style quality frameworks, and system architecture documentation are collected here:

**→ [PUBLICATIONS.md](./PUBLICATIONS.md)**

This includes evaluation dimensions for instruction following, multi-turn coherence, hallucination control, code-review quality, governance gates, and self-healing recovery — suitable for portfolio links and professional evaluation platforms.

## Super Saphira tiers

Premium capability surface and rate limits: [docs/SUPER_SAPHIRA_CAPABILITIES.md](./docs/SUPER_SAPHIRA_CAPABILITIES.md)

| | Super Saphira | Super Saphira Heavy |
|--|---------------|---------------------|
| Messages / 4h | ~100–150 | ~250 |
| DeepSearch / day | ~25–50 | ~100–200 |
| Images / day | ~200 | up to 500 |
| Video / day | ~50 | ~150 |
| Voice session | ~30 min | up to 60 min |

Platform layer (policy, memory, entitlements, workflows): [docs/ADVANCED_PLATFORM.md](./docs/ADVANCED_PLATFORM.md)  
Unified product philosophy: [docs/UNIFIED_WEAVER_BLUEPRINT.md](./docs/UNIFIED_WEAVER_BLUEPRINT.md)  
Everyday life synthesis (Choice / Crisis / Energy / Symptom): [docs/THE_WEAVER_EVERYDAY.md](./docs/THE_WEAVER_EVERYDAY.md)

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
├── skills/                 # Agent skill packages (SKILL.md)
├── docs/                   # Architecture, Weaver, Super tiers, foundations
├── src/                    # Primary runtime (platform API, orchestration)
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

## Key docs

- [PUBLICATIONS.md](./PUBLICATIONS.md) — Publications & Technical Evaluation Frameworks
- [docs/AGENT_ALIGNMENT.md](./docs/AGENT_ALIGNMENT.md) — pipeline and agent roles
- [docs/SUPER_FEATURES_FRAMEWORK.md](./docs/SUPER_FEATURES_FRAMEWORK.md) — Creation / Usage / Upgrade
- [docs/THE_WEAVER.md](./docs/THE_WEAVER.md) — Contextual Cartographer
- [docs/HUMAN_LOGIC_RULEBOOK.md](./docs/HUMAN_LOGIC_RULEBOOK.md) — classical logic verification
- [docs/AI_FOUNDATIONS_STILLNESS_AND_ERROR.md](./docs/AI_FOUNDATIONS_STILLNESS_AND_ERROR.md) — loss, attention, backprop
