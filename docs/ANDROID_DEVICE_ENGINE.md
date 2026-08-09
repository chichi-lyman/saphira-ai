# Saphira Android Device Engine

## Current production boundary

Saphira now has a native Android companion, avatar identity, backend chat bridge, VoiceInteractionService foundation, foreground microphone service, home-screen widget, accessibility bridge, Bluetooth state adapter, proactive WorkManager health worker, and an authenticated WebSocket device-audio gateway.

## 1. Backend

Deploy the FastAPI service behind HTTPS. Required production variables:

- `OPENAI_API_KEY` — backend only; never ship in the APK
- `SAPHIRA_ALLOWED_ORIGINS`
- `SAPHIRA_DEVICE_TOKEN`
- `DATABASE_URL`
- `REDIS_URL`

The public chat endpoint is `/api/chat`, the device audio WebSocket is `/api/device/audio`, and `/health` is the deployment health probe.

## 2. Android endpoint

The Android Gradle build now injects the backend origin through `SAPHIRA_BASE_URL` rather than hard-coding a production URL.

Local/emulator default:

```bash
cd android
gradle assembleDebug --no-daemon
```

For a real device or production backend:

```bash
gradle assembleDebug --no-daemon -PSAPHIRA_BASE_URL=https://your-saphira-backend.example.com
```

Do not put provider API keys, device secrets, or other backend credentials in Android source or resources.

## 3. GitHub Actions APK build

`.github/workflows/android-build.yml` builds `app-debug.apk` on Android changes and uploads the artifact as `saphira-ai-debug-apk`.

For a deployable APK, configure the repository variable `SAPHIRA_BASE_URL` with the HTTPS backend origin. If the variable is absent, CI intentionally builds against the Android emulator bridge (`http://10.0.2.2:8000`) so the build pipeline remains testable without embedding a fake production endpoint.

## 4. Motorola installation

Enable developer options and USB debugging, then install the debug APK with:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Grant microphone and notification permissions. If desired, explicitly enable the Accessibility Service and select Saphira as the Digital Assistant where the Motorola/Android build exposes that option.

## 5. Wake word

The Android project includes an ONNX Runtime dependency and a `WakeWordEngine` boundary for local inference. The trained model is **not** fabricated or committed. Supply a licensed `saphira.onnx` model under `android/app/src/main/assets/wakeword/` and connect its documented tensor contract to the adapter.

Target phrases:

- `Hey Saphira`
- `Okay Saphira`

Until that model is supplied, the app must not claim always-on local wake-word detection.

## 6. Device safety

Accessibility, calls, SMS, system settings, notifications, and external actions must remain explicitly permissioned. High-impact actions should invoke Android confirmation UI and Saphira's autonomy policy rather than silently changing device state.

## 7. Audio pipeline

Target architecture:

`local wake word -> Android capture/AEC -> WSS -> backend STT/realtime adapter -> Saphira Executive Runtime -> tool execution -> streaming TTS -> Android`

The WebSocket endpoint currently validates a server-side device token, accepts bounded PCM frames, and deliberately does not persist raw audio. Provider-specific STT/realtime logic remains behind the `AudioPipeline` adapter.

## 8. Verification gate

Do not mark a capability production-ready until it has passed:

1. APK compilation
2. Runtime permission checks
3. Motorola install/launch
4. Backend HTTPS connectivity
5. Device-token authentication
6. Chat request/response verification
7. WebSocket audio handshake
8. Audio latency and reconnect tests
9. Failure/retry behavior
10. End-to-end device-action verification

## 9. Remaining external inputs

The repository is code-complete up to two assets that cannot be truthfully fabricated:

- a licensed/trained `saphira.onnx` wake-word model
- a production realtime STT/TTS provider implementation and credentials

Deployment also requires an actual HTTPS backend origin and production infrastructure values for the database, Redis, and device token. These are environment-specific operational inputs, not source-code placeholders.
