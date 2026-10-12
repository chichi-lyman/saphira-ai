# Saphira AI — Architecture Completion Integration Guide

© 2026 Chelsea Megan Woods

This package completes the remaining pieces from the Unified Personal AI Operating System specification against the existing `chichi-lyman/saphira-ai` monorepo.

## Files provided

| File | Destination in monorepo | Purpose |
|------|-------------------------|---------|
| `reflection.py` | `workers/reflection.py` | Controlled self-reflection / candidate-build workflow (capture → stage → test → approved promote) |
| `reasoning.py` | `src/core/reasoning.py` | Reasoning matrix, Candidate model, independent verification + resolve |
| `goal_ledger.py` | `src/memory/goal_ledger.py` or `src/orchestration/goal_ledger.py` | Persistent goal ledger (file-backed; swap for PostgreSQL) |
| `agents_router.py` | `src/api/agents_router.py` | Authenticated `/api/agents/tasks` and `/api/agents/plugins/drafts` |
| `flutter_lib/main.dart` | `flutter_project/lib/main.dart` (or mobile Flutter shell) | Floating overlay drawer launcher |

## Integration steps (checklist)

1. **Inspect existing repository** — Already done. Monorepo has orchestrator, swarm, device_ws, self_healing, evolution_engine, PersistentMemoryStore, Celery, Android, commerce policy.

2. **Integrate the API**
   - Copy `agents_router.py` → `src/api/agents_router.py`
   - In `main.py` add:
     ```python
     from src.api.agents_router import router as agents_router
     app.include_router(agents_router, prefix="/api")
     ```
   - Preserve existing `/api/chat`, `/api/device/audio`, health.

3. **Connect persistent memory / goal ledger**
   - Place `goal_ledger.py` under `src/memory/` or `src/orchestration/`.
   - Wire Celery tasks to call `GoalLedger.update_status` with idempotency keys.
   - Production: replace file backend with asyncpg + PostgreSQL + pgvector for embeddings.

4. **Implement actual inference**
   - Existing `device_ws.py` already accepts frames and has an `AudioPipeline` adapter.
   - Connect real STT/TTS providers inside `process_chunk` / response path.
   - Vision: add `/api/device/vision` if not present (mirror the audio session pattern).

5. **Add the Android shell**
   - Use the provided `main.dart` as the Flutter overlay launcher.
   - Merge permissions from the specification into `AndroidManifest.xml` (INTERNET, RECORD_AUDIO, CAMERA, SYSTEM_ALERT_WINDOW, FOREGROUND_SERVICE_*).
   - Follow plugin docs for `flutter_overlay_window` service declaration.
   - iOS remains platform-native; no Android-only overlay assumptions.

6. **Enable controlled self-improvement**
   - Copy `reflection.py` → `workers/reflection.py`.
   - From evolution / self-healing paths, call `capture_exception` on failures.
   - Stage candidates only in isolated workspaces; require explicit `approved=True` for `promote_candidate`.
   - Never hot-reload into the live FastAPI process.

7. **Deploy and validate**
   - Add `SAPHIRA_DEVICE_TOKEN`, `SAPHIRA_PLUGIN_DRAFT_DIR`, Redis/PostgreSQL URLs to environment (never commit secrets).
   - Run existing pytest suite + new tests for goal ledger and reasoning resolve.
   - Verify WebSocket auth, task queue, overlay permission flow, and rollback of candidates.

## Acceptance criteria (from spec)

- Existing web chat and API contracts continue working.
- Audio/vision streams authenticate and bound frames.
- Multi-agent tasks run through durable queue (Celery preferred over pure in-memory).
- Memory/goals per-user, inspectable and deletable.
- Generated code never reaches production without isolated tests + authorization.
- External/financial/destructive actions require explicit approval (already enforced by commerce policy).
- Android overlay is permission-transparent and dismissible.
- Metrics, traces, audit, rollback operational.

## Notes

- Agent names stay internal; surface persona remains warm and non-robotic.
- Model providers are adapters behind the reasoning / orchestrator contracts.
- The reference in-memory task queue is for single-process prototypes only; production must use Celery + Redis + PostgreSQL.

After placing the files, run the test suite and open a PR against `main`.
