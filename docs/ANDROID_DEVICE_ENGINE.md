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

The public chat endpoint is `/api/chat` and the device audio WebSocket is `/api/device/audio`.

## 2. Android endpoint

Set `SAPHIRA_BASE_URL` in `android/app/build.gradle` to the HTTPS backend origin. Do not put provider API keys in Android source or resources.

## 3. Build

From the repository root:

```bash
cd android
gradle assembleDebug --no-daemon
```

The GitHub Actions workflow also builds and uploads `saphira-ai-debug-apk`.

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

## 8. Verification

Do not mark a capability production-ready until it has passed: build, permission, device, backend authentication, latency, failure recovery, and end-to-end task verification tests.
