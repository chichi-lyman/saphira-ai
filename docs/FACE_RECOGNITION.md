# Face Recognition — Saphira AI

© 2026 Chelsea Megan Woods  
Ecosystem: Nova Umbrella™ · Woods AI Studio / Lyman Legacies

## Overview

Saphira can recognize faces through the **Aura** perception agent.  
Design is strictly privacy-first:

- Embeddings are extracted only when the user explicitly requests it.
- Storage happens only after a clear consent step ("Yes, remember this is me / this is Mom").
- Preferred execution path is **on-device** (Android ML Kit / MediaPipe / Flutter).
- Server-side path is available for development and for enrolled identities the user has already approved.

Internal agent names are never shown to the user.

## Architecture

```
Client (camera) 
    → (optional on-device detection / embedding)
    → Aura.perceive({type: "face", image_b64: "...", known_faces: [...]})
    → structured result (matches, requires_consent, …)
    → NovaAethrea (memory) only writes after consent
```

## Python API (Aura)

```python
from agents.aura import AuraAgent

aura = AuraAgent()

# 1. Perception / recognition
result = aura.perceive({
    "type": "face",
    "image_b64": "<base64 jpeg/png>",
    "known_faces": [
        {"label": "Chelsea", "embedding": [...]},
        {"label": "Mom", "embedding": [...]},
    ],
    "return_embeddings": False,   # set True only when enrolling
})

# 2. Enrollment (extract embedding — does NOT store)
enroll = aura.enroll_face(
    image_payload={"image_b64": "..."},
    label="Chelsea",
    consent_token="user-confirmed-abc123",  # required
)
# Memory layer then persists enroll["embedding"] under the label.
```

## Supported Backends (server)

Tried in order:

1. `face_recognition` (dlib) — best quality when installed
2. DeepFace (Facenet)
3. MediaPipe Face Detection + lightweight embedding
4. OpenCV Haar (detection only)

Install optional extras as needed:

```bash
pip install face_recognition   # or
pip install deepface           # or
pip install mediapipe opencv-python-headless
```

## On-Device (recommended for production)

### Android
- Google ML Kit Face Detection + custom FaceNet / MobileFaceNet embedding.
- Or MediaPipe Face Mesh / Face Detection solutions.

### Flutter
- `google_mlkit_face_detection`
- Or `mediapipe` Flutter plugins + local embedding model.

Send only the embedding (or a short list of match scores) to the backend when the user is already authenticated. Never stream raw camera frames continuously.

## Consent Flow (required)

1. Aura detects a face with no confident match → `requires_consent: true`.
2. Saphira asks the user in natural language:  
   “I see someone new. Would you like me to remember this face?”
3. On explicit yes, generate a short-lived consent token and call `enroll_face`.
4. NovaAethrea writes the embedding + label to the explicit fact ledger only.
5. Future perceptions receive the updated `known_faces` list from memory.

## Security Notes

- No background camera access.
- No remote image URL fetching inside Aura (keeps the privacy boundary clean).
- Agent Two can later add liveness / anti-spoof checks before enrollment is accepted.
- All face data is treated as highly sensitive personal data.

## Future Improvements

- Multi-face support in a single frame
- On-device ArcFace / MobileFaceNet ONNX models
- Liveness detection (blink, head-pose) under Agent Two
- Family / household roster management UI
"}, {