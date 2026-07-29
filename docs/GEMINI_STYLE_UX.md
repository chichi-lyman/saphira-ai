# Saphira as a Gemini-Style OS Voice Assistant
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Goal: native **floating** voice UX comparable to Google Gemini — wake word, default assistant slot, overlay sheet, home widget — while keeping Saphira **L1–L3 safety gates** and Samantha dual pipeline.

```
ANDROID OS
  SYSTEM_ALERT_WINDOW | VoiceInteractionService | Wake word service
           |                      |
     Overlay bottom sheet    Home widget
           \                      /
              Saphira Core (persona + Nova agents)
```

## Permissions (Android)

- `SYSTEM_ALERT_WINDOW` — draw over other apps
- `RECORD_AUDIO` — listen / wake word
- `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_MICROPHONE` — background listener

## Triggers

1. **Hey Saphira / Okay Saphira** — Porcupine (or on-device keyword) foreground service
2. **Default Voice Assistant** — `VoiceInteractionService` (home hold / corner swipe when user sets Saphira as default)
3. **Home widget** — one-tap open overlay / app
4. **App icon** — full dashboard (existing Flutter app)

## Autonomy while floating

| Action from overlay | Saphira level |
|---------------------|---------------|
| Chat / explain | L1–L2 (drafts visible) |
| Lights / scenes (pre-allowed) | L2 |
| Unlock / pay / send email | **L1 hard gate** in overlay UI |
| Memory / telemetry | L3 silent |

Overlay must show a **Confirm** chip for L1 actions — never silent unlock from wake word alone.

## SAE Level 4 vs Level 5 (do not confuse with Saphira L3)

| SAE | Meaning | vs Saphira |
|-----|---------|------------|
| **Level 4** | Full automation **only inside** a defined operational design domain (geo-fence, conditions) | Closest analogy: Saphira L2–L3 **inside** user-defined rules (e.g. home scenes) |
| **Level 5** | Full automation **everywhere**, all conditions, no human expected | **Not** Saphira’s goal. Irreversible real-world acts stay L1 |

Saphira L3 ≠ SAE 5. Background memory is not unbounded physical autonomy.

## Flutter / Android file map

| Path | Role |
|------|------|
| `android/.../AndroidManifest.xml` snippets | Permissions + VoiceInteractionService |
| `android/.../SaphiraVoiceInteractionService.kt` | Default assistant hook |
| `android/.../SaphiraWidgetProvider.kt` | Home widget |
| `android/.../res/layout/saphira_widget.xml` | Widget layout |
| `lib/services/wake_word_service.dart` | Porcupine wake word |
| `lib/ui/overlays/saphira_bottom_sheet.dart` | Floating dark luxury sheet |
| `lib/services/autonomy_gate.dart` | L1–L3 checks before execution |
| `lib/widgets/saphira_home_widget.dart` | Widget data bridge |
