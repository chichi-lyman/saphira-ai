# Saphira Android VoiceInteractionService
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

## Purpose

Register Saphira as a **default voice assistant** candidate so Android can invoke her on:

- Assistant gesture / home long-press (when user selects Saphira in system settings)
- Keyguard assist (optional flag in XML)

This mirrors how Gemini / Google Assistant bind into the OS — not a replacement for the Play policy review process.

## Classes

| Class | Role |
|-------|------|
| `SaphiraVoiceInteractionService` | Top-level `VoiceInteractionService` |
| `SaphiraVoiceInteractionSessionService` | Factory for sessions |
| `SaphiraVoiceInteractionSession` | On show → launches `MainActivity` + `openOverlay` |
| `SaphiraRecognitionService` | STT stub; wire to Flutter/Gemini Live later |
| `MainActivity` | Flutter host; MethodChannel `com.saphira.ai/assistant` |

## Flutter

```dart
AssistantChannel.bind(onOpenOverlay: (args) {
  // setState show SaphiraBottomSheetOverlay
  // Do NOT auto-run L1 intents — AutonomyGate still applies
});
```

## User setup on device

1. Install build  
2. Settings → Apps → Default apps → Digital assistant app → **Saphira AI**  
3. Grant mic + display over other apps if using overlay service  

## Safety

Assistant invoke **only opens UI**. Execution still goes through dual pipeline + L1 confirm for unlock/pay/email.
