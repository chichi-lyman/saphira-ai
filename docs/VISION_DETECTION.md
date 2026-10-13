# Vision Object Detection (Aura Perception)

**Status:** Feature branch  
**Owner:** Chelsea Megan Woods  
**Copyright:** © 2026 Chelsea Megan Woods

## Purpose

Extends Saphira's Aura perception layer with optional single-frame object detection. Results are returned both as structured data and as concise text suitable for conversational hand-off and memory storage.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `SAPHIRA_LOCAL_CAMERA_ENABLED` | `false` | Must be `true` to allow any camera access |
| `SAPHIRA_YOLO_MODEL` | `yolov8n.pt` | Model identifier for ultralytics YOLO |

## Endpoints

- `POST /api/vision/detect` — capture one frame and return detections
- `GET /api/vision/health` — capability health check

## Pipeline Placement

Saphira (intent) → **Aura (perception)** → Agent Two (security) → …

Detection runs only under explicit request and never continuously.

## Dependencies (optional)

```
ultralytics>=8.1.0
opencv-python-headless>=4.9.0
```

Add under an optional extras group if the core runtime must remain lean.

## Security Notes

- Camera access is gated by environment flag.
- No autonomous continuous capture.
- Model is loaded once per process.
- Camera handle is always released in a finally block.
