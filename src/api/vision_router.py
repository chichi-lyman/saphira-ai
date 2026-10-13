# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""FastAPI router for Aura vision / object-detection endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.core.vision_detector import DetectionResult, process_camera_frame

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/detect", response_model=DetectionResult)
async def detect_objects(
    camera_index: int = Query(0, ge=0, le=10, description="Camera device index"),
    confidence: float = Query(0.45, ge=0.1, le=0.95, description="Minimum confidence"),
) -> DetectionResult:
    """
    Single-frame object detection for Aura perception.
    Requires SAPHIRA_LOCAL_CAMERA_ENABLED=true. Opt-in only.
    """
    try:
        return process_camera_frame(
            camera_index=camera_index,
            confidence_threshold=confidence,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/health")
async def vision_health() -> dict:
    """Lightweight health check for the vision capability."""
    from src.core.vision_detector import get_detector

    model = get_detector()
    return {
        "status": "ok" if model is not None else "detector_unavailable",
        "camera_enabled": __import__("os").getenv("SAPHIRA_LOCAL_CAMERA_ENABLED", "false"),
    }
