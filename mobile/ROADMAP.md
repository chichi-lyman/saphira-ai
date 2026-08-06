# Saphira AI — Completion Roadmap

**Architected by Chelsea Megan Woods**

## Completed in this phase

| Area | Status |
|------|--------|
| Flutter chat UI + STT + TTS | Done |
| FastAPI /chat + /tts (ElevenLabs) | Done |
| MethodChannel bridge (assistant) | Done |
| VoiceInteractionService + Session overlay | Done |
| Intent router (call, SMS, alarm, open app, nav, settings, flashlight) | Done |
| Android action agent (native intents) | Done |
| Foreground service scaffolding | Done |
| Deployment docs (Railway) | Done |

## Still required for Gemini-replacement quality

### P0 — Assistant role & wake
- [ ] Android Assistant Role registration
- [ ] Default-assistant settings deep-link
- [ ] On-device wake word (Porcupine / custom)
- [ ] Continuous listening only with explicit opt-in + FGS notification

### P1 — Task engine
- [ ] Backend multi-agent orchestrator with tool calling
- [ ] NotificationListenerService
- [ ] Scoped AccessibilityService
- [ ] Calendar/contacts via system APIs
- [ ] WorkManager job queue

### P2 — Memory & streaming
- [ ] Vector memory + RAG
- [ ] User profile / preference learning
- [ ] WebSocket streaming STT → LLM → TTS

### P3 — Platform
- [ ] Quick Settings tile, widget polish
- [ ] Lock-screen assist
- [ ] Motorola battery exemption guidance

### P4 — Production
- [ ] OAuth, Keystore, rate limits, CI/CD, monitoring

## Hard limits on stock Motorola
Silent SMS/calls, full radio toggles without UI, and some system integrations require privileged/OEM status. Saphira can still be the default digital assistant and perform many public-API actions.

© 2026 Chelsea Megan Woods.
