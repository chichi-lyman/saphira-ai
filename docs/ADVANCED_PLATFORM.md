# Saphira Advanced Platform Layer

**Status:** Live on `main` — libraries + HTTP API + tests.
**Still external:** production vector DB, live Matter SDK fabric, full SSO IdP, duplex media server.

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

Includes: autonomy decide, memory, voice, entitlements, devices, identity, evidence, plugins, model routes, **biometrics/analyze**.

## Tests

```bash
pytest -q tests/platform/test_platform_layer.py
# 16 passed
```

## Applied advanced features

- Autonomy levels L1/L2/L3 with stress-aware gate elevation
- Adversarial probe catalog
- Hybrid episodic/semantic memory
- Voice session state machine
- Entitlement metering (Free/Pro/Enterprise)
- RBAC + agent DIDs + API keys
- Hash-chained action receipts + evidence export
- Hierarchical swarm with budget
- Matter L1 unlock safety + offline queue
- Plugin risk-tier sandbox
- Task-class model router
- SDK dry-run capability client
- Multi-signal biometric stress detection (platform API)
