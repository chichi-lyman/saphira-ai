---
name: video-object-detection-fastapi
description: Generate and maintain Python functions that process camera video frames with OpenCV or deep learning models for object detection then format detections as text output for FastAPI endpoints within Saphira AI. Use when extending Aura perception with vision detection pipelines or real-time video analysis endpoints.
---

# Video Object Detection FastAPI (Saphira)

## Overview

Provides templates and procedural guidance for camera-based object detection integrated with Saphira's Aura perception layer and FastAPI surface. Honors the fixed executive pipeline and opt-in hardware access.

## Instructions

When extending vision capabilities:

1. Place core logic under `src/core/vision_detector.py`.
2. Expose endpoints via `src/api/vision_router.py` and register in `main.py`.
3. Keep `SAPHIRA_LOCAL_CAMERA_ENABLED` as the sole gate for camera access.
4. Prefer ultralytics YOLO for modern detection; fall back gracefully when unavailable.
5. Return both human-readable `text_summary` and structured `detections` for hand-off to NovaAethrea or conversational layers.
6. Always release camera handles in finally blocks.
7. Cache the model at process start; never reload per request.
8. Document any new environment variables in `.env.example` and DEPLOY.md notes.

## Resource Usage

- Reference `scripts/example_detector.py` for complete runnable scaffolding.
- Consult `references/best-practices.md` for performance, security, and deployment considerations.
