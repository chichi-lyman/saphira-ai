# Saphira AI — Mobile (Flutter) Build Guide

**Architected by Chelsea Megan Woods**

This directory contains a complete, buildable Flutter application that integrates with your existing FastAPI Saphira backend and incorporates the original Android voice-interaction Kotlin services.

## What This Delivers

- Dark-themed conversational UI with holographic avatar state indicators
- Text + microphone (speech-to-text) input
- Device TTS fallback + backend ElevenLabs proxy support
- Configurable API base URL (stored in SharedPreferences)
- Android voice interaction service stubs ready for system assistant integration

## Quick Start — Build APK

```bash
cd mobile
flutter pub get
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

## Install on Motorola Phone

1. Copy the APK to the phone.
2. Enable Install from unknown sources.
3. Install and open Saphira AI.
4. Open Settings (gear) and set your live FastAPI backend URL.
5. Grant microphone permission.

## Backend Endpoints Expected

- GET / — health
- POST /chat — {"message": "..."} → {"message": "...", "avatar_state": "talking"}
- POST /tts — {"text": "...", "style": "assist"} → audio/mpeg

© 2026 Chelsea Megan Woods. All rights reserved.
