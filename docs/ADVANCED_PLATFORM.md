# Saphira Advanced Platform Layer

**Status:** Scaffold on `main` (libraries + APIs + tests).
**Not yet:** production vector DB, live Matter fabric, SSO/SCIM, duplex media servers.

## Modules (`src/platform/`)

| Area | Path |
|------|------|
| Policy L1/L2/L3 | `policy/autonomy.py` |
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

## HTTP API

Mounted at `/api/platform/*` via `src/api/platform_router.py` (wired in `main.py`).

## Tests

```bash
pytest -q tests/platform/test_platform_layer.py
```
