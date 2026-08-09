# Saphira Repository Sync Map

## Canonical runtime

`chichi-lyman/saphira-ai` is the source of truth for the Saphira executive runtime: conversational entrypoint, task graph, planner, agent registry, executor, autonomy policy, operational memory, capability catalog, tool contracts, and native Android companion.

## Saphira ecosystem repositories

The following repositories are integration surfaces and should not maintain competing orchestration implementations:

- `chichi-lyman/saphira-ai-platform` — platform/deployment surface
- `chichi-lyman/saphira-os` — OS/device adapters
- `chichi-lyman/Saphira-AI-` — Saphira application/assets
- `chichi-lyman/Saphira-ASI-` — ASI experimentation/intelligence surface
- `chichi-lyman/saphira-asi-core` — reusable ASI core components
- `chichi-lyman/saphiras-asi-core` — ASI core variant
- `chichi-lyman/saphira-liaison-ui` — conversational UI
- `chichi-lyman/saphira-sentinel-suite` — security/monitoring
- `chichi-lyman/saphira-twin-vault` — protected identity/memory surface
- `chichi-lyman/saphira-sales-swarm` — sales workers
- `chichi-lyman/v0-saphira-ai` — UI/prototype surface

## Synchronization policy

1. New executive runtime behavior is implemented canonically here first.
2. Integration repositories consume contracts/adapters rather than copying orchestration logic.
3. No API keys or secrets are committed to any repository.
4. Android binaries never contain provider API keys.
5. External side effects require Saphira autonomy/approval policy.
6. CI should validate compatibility between integration surfaces and the canonical runtime.

## Current native Android path

`android/` contains the native companion. It communicates with Saphira through a backend endpoint and keeps provider credentials server-side.
