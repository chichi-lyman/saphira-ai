# Saphira Ecosystem — Current Build Status (Updated)

## Source of truth
`chichi-lyman/saphira-ai` remains the canonical runtime repository.

## Runtime layers (updated)
- Conversational executive interface
- Task planning and delegation
- Capability-based agent registry
- Background execution contracts
- Autonomy and approval policy
- Operational memory (NovaAethrea)
- Tool / integration boundary
- Android companion boundary
- **Always-on wake-word + barge-in voice stack**
- **Autonomous evolution & self-healing loop**

## Native Android
Native project under `android/` with Kotlin/Compose, speech/TTS foundations, backend bridge, VoiceInteractionService scaffolding, and the new `SaphiraHardwareReceiver` for telephony / Bluetooth muting.

## New / upgraded capabilities
| Capability | Status |
|------------|--------|
| Real-time voice streaming & interruption handling | Operational (wake_word + interruption_orchestrator) |
| Android device-control adapters (mic mute on call / BT) | Active / scaffolding integrated |
| Always-on wake phrases (“okay saphira”, “hey saphira”, “saphira”) | Implemented |
| Self-healing audio / stream recovery | Implemented via evolution_engine |
| Daily measured optimisation (+1 % rule) | Implemented (bounded, non-safety parameters only) |
| Custom openWakeWord training path | Documented + orchestration script |

## Production blockers (remaining)
1. Deploy a public HTTPS Saphira backend endpoint.
2. Store provider credentials only in backend secret storage.
3. Replace Android placeholder backend URL through release configuration.
4. Complete production OAuth for external services that require user authorisation.
5. Sign and distribute the Android build.
6. End-to-end tests on target Motorola (and Chromebook) devices with real Bluetooth headsets.

## Security rule
Never commit API keys, OAuth refresh tokens, signing keys, or other secrets to source control. Rotate any credential previously exposed.

© 2026 Chelsea Megan Woods. All rights reserved.
