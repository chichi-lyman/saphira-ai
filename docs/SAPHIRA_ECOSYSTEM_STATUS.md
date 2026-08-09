# Saphira Ecosystem — Current Build Status

## Source of truth

`chichi-lyman/saphira-ai` is the canonical Saphira runtime repository.

## Runtime layers

- Conversational executive interface
- Task planning and delegation
- Capability-based agent registry
- Background execution contracts
- Autonomy and approval policy
- Operational memory
- Tool/integration boundary
- Android companion boundary

## Native Android

The repository contains the native Android project under `android/` with Kotlin/Compose, Android speech/TTS foundations, backend bridge, and VoiceInteractionService scaffolding.

The Android application intentionally contains no provider API keys. Provider credentials belong on the trusted backend.

## CI

`.github/workflows/saphira-ci.yml` validates Python compilation and, when the Android Gradle project is present, assembles a debug APK.

## Production blockers

1. Deploy a public HTTPS Saphira backend endpoint.
2. Store provider credentials only in backend secret storage.
3. Replace the Android placeholder backend URL through release configuration.
4. Complete production OAuth for external services that require user authorization.
5. Add Android device-control adapters with explicit permissions.
6. Add real-time voice streaming and interruption handling.
7. Run end-to-end tests on the target Motorola device.
8. Sign and distribute the Android build.

## Security rule

Never commit API keys, OAuth refresh tokens, signing keys, or other secrets to source control. Any credential previously pasted into chat or another public surface should be rotated.
