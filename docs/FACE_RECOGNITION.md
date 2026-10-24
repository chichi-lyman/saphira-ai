# Face Recognition — Saphira AI

© 2026 Chelsea Megan Woods  
Ecosystem: Nova Umbrella™ · Woods AI Studio / Lyman Legacies

## Overview

Saphira can recognize faces through the **Aura** perception agent and store consented identities via **NovaAethrea**.  
Design is strictly privacy-first:

- Embeddings are extracted only when the user explicitly requests it.
- Storage happens only after a clear consent step ("Yes, remember this is me / this is Mom").
- Preferred execution path is **on-device** (Android ML Kit).
- Server-side path is available for development and for enrolled identities the user has already approved.

Internal agent names are never shown to the user.

## Architecture

```
Client (camera + ML Kit)
    → crop face JPEG (base64)
    → POST /api/face/perceive
    → Aura matches against NovaAethrea known faces
    → if unknown → Saphira asks for consent
    → POST /api/face/consent-token  (only after user says yes)
    → POST /api/face/enroll
    → NovaAethrea writes embedding to explicit fact ledger
```

## REST API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/face/perceive` | Detect + recognize against stored faces |
| POST | `/api/face/enroll` | Extract + store embedding (requires consent_token) |
| GET  | `/api/face/list` | List remembered labels (no embeddings) |
| DELETE | `/api/face/forget/{label}` | Remove a stored face |
| POST | `/api/face/consent-token` | Generate one-time consent proof |

### Perceive example

```bash
curl -X POST https://your-backend/api/face/perceive \
  -H "Content-Type: application/json" \
  -d '{"image_b64": "<base64 jpeg>", "return_embeddings": false}'
```

### Enroll flow

1. User says "yes, remember this face as Chelsea"
2. Client calls `POST /api/face/consent-token` → receives token
3. Client calls `POST /api/face/enroll` with image, label, and token

## Python API (Aura + NovaAethrea)

```python
from agents.aura import AuraAgent
from agents.novaaethrea import NovaAethreaAgent

aura = AuraAgent()
memory = NovaAethreaAgent()

# Perceive
result = aura.perceive({
    "type": "face",
    "image_b64": "<base64>",
    "known_faces": memory.get_known_faces_for_perception(),
})

# Enroll after consent
enroll = aura.enroll_face(
    image_payload={"image_b64": "..."},
    label="Chelsea",
    consent_token="user-confirmed-token",
)
memory.store_face(
    label="Chelsea",
    embedding=enroll["embedding"],
    consent_token="user-confirmed-token",
)
```

## On-Device (Android)

- `FaceRecognitionHelper.kt` — ML Kit face detection + face crop to base64 JPEG
- `SaphiraApi.kt` — `perceiveFace`, `requestConsentToken`, `enrollFace`, `listFaces`
- Camera permission is declared; use only on explicit user action (never continuous background)

### Typical client flow

```kotlin
val helper = FaceRecognitionHelper(context)
val result = helper.detect(bitmap, includeCropBase64 = true)
val faceB64 = result.faceJpegBase64 ?: return

// Recognize
val perception = api.perceiveFace(faceB64).getOrThrow()
if (perception.optBoolean("requires_consent")) {
    // Ask user in natural language via Saphira
    // On yes:
    val token = api.requestConsentToken().getOrThrow()
    api.enrollFace(faceB64, label = "Chelsea", consentToken = token)
}
```

## Server backends (optional)

Tried in order by Aura:

1. `face_recognition` (dlib)
2. DeepFace (Facenet)
3. MediaPipe
4. OpenCV Haar (detection only)

Install only what you need:

```bash
pip install opencv-python-headless mediapipe numpy
# or
pip install face_recognition
# or
pip install deepface
```

## Security & Privacy Rules

- No continuous camera access.
- No remote image URL fetching inside Aura.
- Face data treated as highly sensitive; stored only after explicit consent.
- Consent token is required on enroll; generate it only after the user says yes.
- Agent Two can later add liveness / anti-spoof checks before enrollment is accepted.

## Future Improvements

- Multi-face support in a single frame
- On-device ArcFace / MobileFaceNet ONNX models (embeddings stay local)
- Liveness detection under Agent Two
- Family / household roster management UI
