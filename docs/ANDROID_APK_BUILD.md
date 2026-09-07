# Saphira AI Android APK Build

Saphira already contains a native Android/Jetpack Compose application under `android/`. This is not a browser-only wrapper: the Android client includes conversational UI, speech recognition, text-to-speech, notifications, WorkManager, foreground voice service hooks, accessibility hooks, and a widget/assistant surface.

## Cloud build

The GitHub Actions workflow is:

`.github/workflows/android-build.yml`

Before running it, configure the repository variable:

`SAPHIRA_BASE_URL=https://YOUR-LIVE-SAPHIRA-BACKEND`

The backend must expose:

`POST /api/chat`

The Android client already calls that route and expects the JSON `message` response field.

## Run the build

1. Open GitHub → Actions.
2. Select **Saphira Android Build**.
3. Choose **Run workflow**.
4. Wait for **Build Saphira Android APK** to finish successfully.
5. Open the completed run.
6. Download the `saphira-ai-apk` artifact.
7. Extract the ZIP and install `app-debug.apk` on the Android device.

## Important signing distinction

The workflow intentionally produces an **installable debug APK**. It is suitable for direct device testing and sideloading.

A Play Store release should use a persistent release keystore stored as GitHub encrypted secrets. Do not generate a new signing key for every build; doing so would prevent normal app updates from being installed over the previous release.

## Current Android toolchain

- Android Gradle Plugin: 8.7.3
- Kotlin: 2.0.21
- Kotlin Compose compiler plugin: 2.0.21
- Compile/target SDK: 35
- Minimum SDK: 26
- Java: 17
- Gradle: 8.11.1
- Application ID: `ai.saphira.mobile`

## Backend contract

The Android app sends:

```json
{"message":"Hello Saphira"}
```

to:

`/api/chat`

The FastAPI chat router mounted by `main.py` provides this route and returns a response containing `message`.

## Security

Do not place OpenAI, Gemini, Stripe, database, Resend, Telegram, or other provider secrets in the APK. The APK contains only the public Saphira backend origin. Provider credentials remain server-side.
