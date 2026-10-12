# Saphira AI — Live Capability Audit and Phase 1 Gate

Date: 2026-10-12

## Evidence standard

This audit separates repository evidence from runtime evidence. A class, README entry, agent directory, capability contract, or committed adapter does not by itself prove a capability is live. **LIVE** requires configured credentials, a successful target-environment health check, passing integration tests, permission enforcement, audit telemetry, and a verified end-to-end task. Since this repository inspection did not execute the deployed runtime or CI, no external provider is marked LIVE by this document.

## Initial repository findings

| Capability | Repository evidence | Initial status | Evidence still required |
|---|---|---|---|
| Specialist registry | `src/core/specialist_registry.py` | Code present; runtime status unverified | Registry wired into startup, unit/integration tests, health and audit events |
| Plugin registry | `src/integrations/plugin_registry.py` | Code present; individual plugin status unverified | Per-plugin credentials, health checks, permission scopes, tests |
| Satellite registry | `src/integrations/satellite_registry.py` | Catalog/adapter declarations present | Each satellite repository and configured adapter verified individually |
| Governance manifests | `governance/policies.py` | Policy implementation present | Deny/approval tests and proof all execution paths invoke policy |
| Platform router | `src/api/platform_router.py` | Router implementation present | App startup wiring, endpoint tests, live deployment smoke test |
| Model registry/routing contract | `src/core/model_registry.py` | Added in Phase 1 foundation | Adapter registration from configuration, app wiring, CI run |
| Operational telemetry primitives | `src/core/operational_telemetry.py` | Added in Phase 1 foundation | Exporter, durable storage, dashboard, and production instrumentation |
| Model provider API access | Provider-specific wiring must be inspected per provider | Planned/unverified | Secret configured, authenticated health check, request/response integration test |
| 20+ simultaneous model endpoints | Target requirement | Planned until measured | Verified adapter for each endpoint, quota/cost controls, concurrency tests |
| Voice calls and messaging | External connectors are provider/platform dependent | Planned/unverified | Consent, identity disclosure, opt-out, permissions, audit and end-to-end tests |
| Image/video/audio generation | External providers required | Planned/unverified | Working provider, rights/consent policy, usage/cost telemetry, generated-output test |

## Phase 1 gateway contract

The initial provider-neutral contract is implemented in `src/core/model_registry.py`.

- `ModelSpec` records provider/model identity, capabilities, modalities, enablement, declared cost, and latency.
- `RoutingRequest` declares capability, modalities, cost/latency bounds, and provider preference.
- `ModelRegistry` supports registration, discovery, deterministic filtering/ranking, and invocation through an injected adapter callable.
- No network call or provider credential is performed by the registry itself.
- A model is not eligible unless it is explicitly enabled and meets the request constraints.
- Unknown cost/latency is not treated as a known value when the caller sets a corresponding hard bound.
- Provider adapters must be wired by the host application after configuration and health validation.

## Operational telemetry contract

The initial metrics accumulator is implemented in `src/core/operational_telemetry.py`. It reports:
- operation count and success rate;
- average latency and approximate p95 latency;
- estimated cost total and average per operation;
- verification pass rate, excluding operations with unknown verification status;
- per-provider/model breakdown.

This is an in-process primitive, not yet a durable production dashboard. Next integration work should export sanitized events to the configured metrics/storage backend and add alerting. Do not log prompts, outputs, secrets, or personal data as metric labels. Estimated cost must be computed from provider usage/pricing data where available; never present estimates as billed amounts.

## Verification checklist

- [ ] Run `uv run pytest` or `pytest` in the repository environment.
- [ ] Run `ruff check src/core/model_registry.py src/core/operational_telemetry.py tests/test_model_registry_telemetry.py`.
- [ ] Wire registry creation and adapter registration into application startup.
- [ ] Add per-provider health checks that validate credentials without logging them.
- [ ] Add an integration test using a mock adapter, then an opt-in smoke test for each real provider.
- [ ] Instrument every model invocation with operation/task IDs, provider/model, latency, success/failure, verification result, and usage-derived cost.
- [ ] Persist events and expose dashboard/API metrics with access controls and retention limits.
- [ ] Verify policy checks happen before side-effecting tool calls.
- [ ] Only then mark each individual adapter LIVE.

## Rollout gate

External API connectors remain disabled by default until the registry, permission policy, telemetry, and test suite are wired into the runtime. Enable providers one at a time with explicit configuration, budgets, rate limits, and rollback.
