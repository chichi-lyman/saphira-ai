# Saphira AI End-to-End Wake-Word & WebSocket Pipeline

© 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella

The architecture pipeline for Saphira AI is fully integrated on `main`.

## System diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      ANDROID ON-DEVICE CLIENT LAYER                       │
│                                                                           │
│  ┌───────────────────────┐   16 kHz Audio   ┌──────────────────────────┐  │
│  │   Microphone Stream   ├─────────────────►│ SaphiraWakeWordEngine    │  │
│  └───────────────────────┘                  │ (ONNX openwakeword)      │  │
│                                             └────────────┬─────────────┘  │
│                                                          │ > 0.75 Score   │
│                                                          ▼                │
│  ┌───────────────────────┐  com.saphira.ai/ ┌──────────────────────────┐  │
│  │ SaphiraVoiceClient    │◄─────────────────┤ BroadcastReceiver        │  │
│  │ (Flutter WS Client)   │  wakeword_events │ (MainActivity.kt)        │  │
│  └───────────┬───────────┘                  └──────────────────────────┘  │
└──────────────┼────────────────────────────────────────────────────────────┘
               │
               │ ws://<host>:<port>/v1/saphira/stream?session_id=...
               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND ORCHESTRATOR                         │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ main.py (FastAPI Primary Entrypoint)                                │  │
│  │ └── saphira_dispatcher_router (/v1/saphira/stream)                  │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ NovaAgentRegistry & Execution Pipeline                              │  │
│  │ ├── Saphira     ──► Personal AI Assistant & Intent Orchestrator     │  │
│  │ ├── Aura        ──► Audio, Voice & Speech Processing                │  │
│  │ ├── Agent Two   ──► Vector Memory Ledgers & Context Router          │  │
│  │ └── NovaReign   ──► Android Accessibility & System Executor         │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
└─────────────────────────────────────┼─────────────────────────────────────┘
                                      │
                                      │ requires_client_action: true
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     NATIVE SYSTEM AUTOMATION LAYER                        │
│                                                                           │
│  ┌───────────────────────────────┐        ┌────────────────────────────┐  │
│  │ SaphiraAccessibilityBridge    ├───────►│ SaphiraAccessibilityService│  │
│  │ (Flutter Channel)             │        │ (Clicks, Taps, Text Injection)│
│  └───────────────────────────────┘        └────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Implementation milestones locked on `main`

* **On-Device Wake-Word Detection** — `SaphiraWakeWordEngine.kt` processes local 16 kHz PCM frames in 80 ms chunks via ONNX Runtime without touching cloud bandwidth or battery unnecessarily.
* **Native Event Transport** — `MainActivity.kt` captures `com.saphira.ai.WAKEWORD_TRIGGERED` broadcasts and pipes confidence metrics to Flutter’s `wake_word_listener.dart` via EventChannel.
* **Unified Backend Gateway** — `saphira_dispatcher.py` operates as an `APIRouter` mounted directly onto the primary `main.py` entrypoint, routing WebSocket sessions across Nova Umbrella sub-agents.
* **Persistent Foreground Execution** — `SaphiraForegroundService.kt` maintains `START_STICKY` execution in the notification tray to preserve background voice streams and accessibility triggers when the screen is locked or other apps are active.

## Key paths

| Layer | Path |
|-------|------|
| ONNX engine | `android/app/src/main/kotlin/com/saphira/ai/SaphiraWakeWordEngine.kt` |
| Foreground service | `android/app/src/main/kotlin/com/saphira/ai/SaphiraForegroundService.kt` |
| EventChannel bridge | `android/app/src/main/kotlin/com/saphira/ai/MainActivity.kt` |
| Flutter listener | `flutter_project/lib/services/wake_word_listener.dart` |
| WebSocket dispatcher | `src/api/saphira_dispatcher.py` |
| FastAPI entrypoint | `main.py` |
| Model asset | `android/app/src/main/assets/saphira_wakeword.onnx` |

## Physical device verification

```bash
# 1. Sync dependencies and run on hardware
cd flutter_project
flutter pub get
flutter run
```

```dart
// 2. Initial launch sequence in Flutter
void initializeSaphiraApp() async {
  // Request system overlay permissions for floating HUD/Voice actions
  await SaphiraForegroundServiceBridge.requestOverlayPermission();

  // Start sticky background foreground service & voice loop
  await SaphiraForegroundServiceBridge.startService();

  // Initialize local wake-word channel listener
  final wakeWordListener = SaphiraWakeWordListener();
  wakeWordListener.initialize(
    'ws://YOUR_FASTAPI_IP:8000/v1/saphira/stream?session_id=android_main',
  );
}
```

1. Place the trained model at `android/app/src/main/assets/saphira_wakeword.onnx`.
2. Point the listener at your FastAPI host (use the device’s reachable LAN IP, not `localhost`).
3. Say **“Saphira”** and confirm the WebSocket handshake opens automatically after local confidence exceeds 0.75.
