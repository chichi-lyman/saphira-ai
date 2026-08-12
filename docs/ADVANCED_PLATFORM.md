# Saphira Advanced Platform Layer

**Status:** Scaffold landed on `main` (platform APIs + libraries + tests).
**Not yet:** full production backends (vector DB, live Matter fabric, SSO/SCIM IdP, duplex media servers).

See repository modules under `src/platform/` and HTTP routes under `/api/platform/*`.

## Tests

```bash
pytest -q tests/platform/test_platform_layer.py
```
