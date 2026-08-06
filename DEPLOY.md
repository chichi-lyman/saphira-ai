# Saphira AI — FastAPI Backend Deployment Guide

**Architected by Chelsea Megan Woods**

## Fastest Path: Railway (already configured)

Your repository already contains `railway.json` and a working Dockerfile.

### Steps

1. Go to [railway.app](https://railway.app) and create a new project.
2. Choose **Deploy from GitHub repo** → select `chichi-lyman/saphira-ai`.
3. Railway will detect the Dockerfile and build automatically.
4. In the service **Variables** tab, add at minimum:

```
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=your_cloned_voice_id
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
SAPHIRA_TTS_PROVIDER=elevenlabs
GEMINI_API_KEY=...          # or OPENAI_API_KEY / XAI_API_KEY
ENVIRONMENT=production
```

5. After deploy, copy the public URL (e.g. `https://saphira-ai-production.up.railway.app`).
6. Paste that URL into the Saphira mobile app Settings → Backend API Base URL.

### Verify

```bash
curl https://YOUR-RAILWAY-URL/
curl https://YOUR-RAILWAY-URL/tts/status
```

## ElevenLabs Setup (Chelsea Voice Clone)

1. Create an ElevenLabs Instant Voice Clone using your voice samples.
2. Copy the Voice ID.
3. Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID as environment variables.
4. Test: POST /tts with {"text":"Hello, I am Saphira.","style":"assist"}

## Ownership

© 2026 Chelsea Megan Woods. All rights reserved.
