# Saphira AI — First-Party Merge Policy

## Objective

Make `chichi-lyman/saphira-ai` the canonical executive runtime while preserving useful first-party projects as modular satellites where wholesale merging would create unnecessary risk.

## Merge classes

### P0 — integrate now

Code that directly strengthens the production Saphira runtime:

- `saphira-asi-core`
- `saphira-os`
- `saphira-ai-platform`
- `saphira-sales-swarm`
- `saphira-sentinel-suite`
- `saphira-twin-vault`
- `agent-zero` as an isolated execution worker

### P1 — connect behind adapters

Capabilities that should be callable by the executive runtime without being copied wholesale:

- Saphira UIs
- agent workers
- NovaReign/NovaAethrea/Aura components
- Nova Umbrella orchestration
- NexusAgent
- Agent Skills
- Termux/device execution
- Chelsea Sales
- Supabase chat patterns

### P2 — selectively extract after review

General-purpose or specialized tooling whose useful components can be adapted later:

- geospatial MCP
- SDKs
- deployment plugins
- legacy assistant implementations
- device-assistant references

### Hold — do not copy wholesale

Large, third-party-derived, unrelated, or independently deployable repositories remain separate until license, provenance, dependency, security, and architecture review is complete.

## Required checks before code extraction

1. Repository provenance and license review.
2. Dependency and vulnerability scan.
3. Secrets and credential scan.
4. Duplicate implementation detection.
5. API/runtime compatibility review.
6. Tenant isolation review.
7. Permission and side-effect review.
8. Unit/integration test coverage.
9. Performance and resource impact assessment.
10. Rollback path.

## Architectural rule

The master repository owns identity, executive orchestration, capability discovery, policy, verification, memory boundaries, observability, and integration contracts. Satellite projects provide specialized implementations.

This avoids turning Saphira into a monolithic repository while still making the whole first-party portfolio available as one unified intelligence system.
