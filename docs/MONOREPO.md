# Monorepo guide

© 2026 Chelsea Megan Woods

## Why

One dependency set, one CI pipeline, one version line for Saphira + all agents.

## Dependency management

| File | Role |
|------|------|
| `requirements.txt` | Runtime (unified) |
| `requirements-dev.txt` | Includes runtime + pytest/ruff/mypy/bandit |
| `pyproject.toml` | Package metadata, tool config, optional extras |
| `Makefile` | `make install` / `make ci` / `make test` |

Install once at the root; all packages under `agents/` and `packages/` share the environment.

## Pipelines

- **Monorepo CI** (`.github/workflows/ci.yml`): install → lint → security → full pytest  
- **Agent matrix**: import smoke test per agent package  

## Relationship to standalone repos

Historical repos (`agent-apex`, `novaaethrea-agent`, …) can stay as public identity pages. New code and dependency changes should land **here** first.

## Pipeline order (runtime)

Saphira → Aura → Agent Two → NovaReign → NovaAethrea → Agent Zero  
Specialists (Apex, Instinct, Lexis, Cipher, Scholar, Lyra) dispatched from NovaReign.
