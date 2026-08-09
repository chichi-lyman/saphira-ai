# Saphira Android

Native Android companion for Saphira AI.

## Architecture

- Native Kotlin Android client
- Voice input through Android SpeechRecognizer
- Native Text-to-Speech response
- Saphira backend bridge through HTTPS
- Android VoiceInteractionService scaffold for default-assistant integration
- No OpenAI/API credentials are stored in the APK

## Backend configuration

Set `SAPHIRA_BASE_URL` in `android/app/build.gradle` to the deployed HTTPS Saphira backend before building. The placeholder is intentional.

The Android app must never contain the OpenAI API key. The key belongs only on the trusted Saphira backend.

## Motorola setup

1. Build and install the Android app.
2. Grant microphone permission.
3. Set the Saphira backend URL.
4. Select Saphira as the phone's digital assistant if the device exposes the VoiceInteractionService.
5. Grant only the Android permissions required for the features you enable.

## Current boundary

This first native layer provides the phone UI, voice loop, backend bridge, and assistant-service foundation. Full device automation, screen interaction, proactive background execution, and production voice streaming require additional Android permission adapters and backend tool integrations.
