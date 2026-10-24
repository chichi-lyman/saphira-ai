# Saphira Advanced Platform Layer

**Status:** Live on `main` — libraries + HTTP API + tests.  
**Still external:** production vector DB, live Matter SDK fabric, full SSO IdP, duplex media server.

## Super Saphira tiers (surface)

Premium plans and quotas are defined in entitlements metering and documented in [SUPER_SAPHIRA_CAPABILITIES.md](./SUPER_SAPHIRA_CAPABILITIES.md).

| Feature / Limit | Standard Super Saphira | Super Saphira Heavy |
|-----------------|------------------------|---------------------|
| Messages / 4h | ~100–150 | ~250 |
| DeepSearch / day | ~25–50 | ~100–200 |
| Images / day | ~200 | up to 500 |
| Video clips / day | ~50 | ~150 |
| Voice session | ~30 min | up to 60 min |
| Priority compute | standard | priority + early features |
| Workflow runs / day | metered | higher tier quota |

Plan keys: `super_saphira`, `super_saphira_heavy` in `src/platform/entitlements/metering.py`.

Capability keys for Imagine image/video and Think Mode live in `src/core/saphira_capability_catalog.py` (`imagine.image`, `imagine.video`, `think.mode`).

Unified product philosophy: [UNIFIED_WEAVER_BLUEPRINT.md](./UNIFIED_WEAVER_BLUEPRINT.md).

## Modules (`src/platform/`)

| Area | Path |
|------|------|
| Policy L1/L2/L3 (+ stress elevation) | `policy/autonomy.py` |
| Adversarial probes | `policy/adversarial.py` |
| Hybrid memory | `memory/hybrid.py` |
| Voice sessions | `voice/streaming.py` |
| Entitlements | `entitlements/metering.py` |
| RBAC / API keys | `identity/rbac.py` |
| Evidence / receipts | `evidence/` |
| Hierarchical swarm | `swarm/hierarchy.py` |
| Matter L1 + offline | `devices/` |
| Plugin sandbox | `plugins/sandbox.py` |
| Model router | `observability_ext/model_router.py` |
| SDK | `sdk/client.py` |
| Biometrics (stress) | `biometrics/stress.py` |

## HTTP API

Mounted at `/api/platform/*` via `src/api/platform_router.py` (wired in `main.py`).

Includes: autonomy decide, memory, voice, entitlements, devices, identity, evidence, plugins, model routes, biometrics/analyze, **multi-agent workflows** (`/workflows/run`, research-code-validate, analyze-architect-review, secure-delivery, creative/weaver templates when enabled).

Workflow runs consume `workflow_runs_per_day` (and related) entitlement metrics.

## Tests

```bash
pytest -q tests/platform/test_platform_layer.py
```

## Applied advanced features

- Autonomy levels L1/L2/L3 with stress-aware gate elevation
- Adversarial probe catalog
- Hybrid episodic/semantic memory
- Voice session state machine
- Entitlement metering (Free/Pro/Enterprise + Super Saphira tiers)
- RBAC + agent DIDs + API keys
- Hash-chained action receipts + evidence export
- Hierarchical swarm with budget
- Matter L1 unlock safety + offline queue
- Plugin risk-tier sandbox
- Task-class model router
- SDK dry-run capability client
- Multi-signal biometric stress detection (platform API)
- Multi-agent workflow engine + custom skills (reviewer, architect, analyst, security auditor, creative, weaver)

## Related

- [SUPER_SAPHIRA_CAPABILITIES.md](./SUPER_SAPHIRA_CAPABILITIES.md)
- [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md)
- [MULTI_AGENT_WORKFLOWS.md](./MULTI_AGENT_WORKFLOWS.md)
- [UNIFIED_WEAVER_BLUEPRINT.md](./UNIFIED_WEAVER_BLUEPRINT.md)
