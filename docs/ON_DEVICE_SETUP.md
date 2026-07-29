# On-Device Setup — Floating Saphira Assistant
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

## 1. Merge AndroidManifest

Copy permissions + services from `android/app/src/main/AndroidManifest.saphira_snippets.xml` into your real `AndroidManifest.xml`.

Set default assistant: **Settings → Apps → Default apps → Digital assistant app → Saphira AI**

## 2. Picovoice wake word

1. console.picovoice.ai → AccessKey  
2. Train **Hey Saphira** / **Okay Saphira** for Android → `.ppn`  
3. Save to `assets/wake_words/Hey-Saphira_en_android.ppn`  
4. Register asset in `pubspec.yaml`  
5. Pass key into `WakeWordService.initWakeWord`

## 3. Chelsea voice (Saphira TTS)

1. ElevenLabs → clone **your** voice  
2. `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` on backend  
3. Flutter: `SaphiraTts(backendTtsUrl: 'https://.../api/v1/tts')`  
4. After Samantha pipeline text → `speakUrl(samanthaSpeech, style: 'assist')`

## 4. Assistant channel

```dart
AssistantChannel.bind(onOpenOverlay: (args) {
  // show SaphiraBottomSheetOverlay
  // AutonomyGate before any L1 intent
});
```

Native: `MainActivity` + `SaphiraVoiceInteractionSession` already invoke `openOverlay`.

## 5. Pipeline

Spoken text → backend `/chat` or local orchestrator → dual pipeline (`saphira_translator`) → public string → **Chelsea TTS** → speaker.

L1: show Confirm chip; only then execute.
