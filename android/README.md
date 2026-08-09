# Saphira Android

Native Android companion for Saphira AI Production.

## What this app is

The phone-facing client for Saphira: one conversational assistant on the surface, with Saphira's autonomous agents remaining behind the backend. The app includes the supplied Saphira portrait as her identity/avatar, chat, speech recognition, spoken responses, secure HTTPS backend bridging, and a VoiceInteractionService foundation for supported Android devices.

## Security boundary

- No OpenAI or provider API keys are stored in the APK.
- The Android client talks to the trusted Saphira backend.
- External/destructive actions must be approved by the backend autonomy policy.

## Backend configuration

Set `SAPHIRA_BASE_URL` to the deployed HTTPS Saphira backend before building. The placeholder is intentional until the production backend URL exists.

## Motorola setup

1. Build the debug APK from the GitHub Actions `saphira-ai-debug-apk` artifact or Android Studio.
2. Install it on the Motorola phone.
3. Grant microphone and notification permissions as requested.
4. Configure the Saphira backend URL.
5. Select Saphira as the phone's digital assistant if the Motorola/Android build exposes the VoiceInteractionService option.
6. Grant only the device permissions required by enabled capabilities.

## Current boundary

This native layer provides the first real phone interface, avatar, voice loop, backend bridge, and assistant-service foundation. Full device automation, screen interaction, proactive background execution, and production low-latency voice streaming require their corresponding Android permission adapters and backend tool integrations.
