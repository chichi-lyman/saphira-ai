# A–E Implementation Notes

**Branch:** `feat/nova-umbrella-stress-test-and-integration`  
**Date:** 2026-10-20  
**Author:** Chelsea Megan Woods

## A — Memory paths through TenantMemoryGuard
- `src/platform/memory/enforced.py` — `remember` / `recall` / `forget` API
- Agents and workflows should import from `enforced`, not raw `hybrid.memory_store`

## B — Model router → provider_registry
- `src/core/provider_router.py` — `ProviderModelRouter.choose()` uses OpenAI / Azure / Bedrock / Gemini / xAI / local
- Live HTTP calls remain in existing router clients; this module is the selection authority

## C — Entitlements in RESERVE
- `src/commerce/reserve_entitlements.py` — `EntitlementMeter.can_reserve` / `commit_usage`
- LeadOS bridge checks meter before scoring runs

## D — LeadOS → state machine + test checkout
- `src/commerce/leados_state_bridge.py` — score, present_offer, create_test_checkout, activate_with_stripe_event
- `test_mode=True` by default (no live Stripe)

## E — Matrix Level-1
- `tests/matrix/test_level1_functional.py` — functional policy, tenant, entitlements, provider status, matrix snapshot

## Run
```bash
pytest -q tests/matrix/test_level1_functional.py tests/platform/test_tenant_memory.py tests/commerce/test_leados_execution_contract.py
```
