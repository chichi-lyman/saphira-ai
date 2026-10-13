# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Camera frame object detection helpers for Aura perception layer.

Opt-in only. Respects SAPHIRA_LOCAL_CAMERA_ENABLED.
Integrates with the fixed pipeline under Aura (perception).
"""

from __future__ import annotations

import logging
import os
from typing import Any, List, Optional

import cv2
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger("saphira.perception.vision")


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: List[float]  # [x1, y1, x2, y2]


class DetectionResult(BaseModel):
    text_summary: str
    detections: List[Detection]
    frame_shape: Optional[List[int]] = None


def _load_yolo_model() -> Any:
    """Lazy-load ultralytics YOLO (preferred) or return None."""
    try:
        from ultralytics import YOLO

        model_name = os.getenv("SAPHIRA_YOLO_MODEL", "yolov8n.pt")
        model = YOLO(model_name)
        logger.info("YOLO model '%s' loaded for vision detection", model_name)
        return model
    except Exception as exc:
        logger.warning(
            "ultralytics unavailable (%s); object detection disabled until configured",
            exc,
        )
        return None


_MODEL: Any = None


def get_detector() -> Any:
    global _MODEL
    if _MODEL is None:
        _MODEL = _load_yolo_model()
    return _MODEL


def decode_detections(raw: Any, confidence_threshold: float = 0.45) -> List[Detection]:
    """Convert model output into a list of Detection objects."""
    detections: List[Detection] = []
    if raw is None:
        return detections
    for result in raw:
        if not hasattr(result, "boxes") or result.boxes is None:
            continue
        names = getattr(result, "names", {}) or {}
        for box in result.boxes:
            conf = float(box.conf)
            if conf < confidence_threshold:
                continue
            cls_id = int(box.cls)
            label = names.get(cls_id, f"class_{cls_id}")
            xyxy = box.xyxy[0].tolist()
            detections.append(Detection(label=label, confidence=conf, bbox=xyxy))
    return detections


def format_detections_as_text(detections: List[Detection]) -> str:
    if not detections:
        return "No objects detected above confidence threshold."
    parts = [f"{d.label} ({d.confidence:.2f})" for d in detections]
    return f"Detected {len(detections)} object(s): " + ", ".join(parts)


def process_camera_frame(
    camera_index: int = 0,
    confidence_threshold: float = 0.45,
) -> DetectionResult:
    """
    Capture one frame, run object detection, and return structured + text output.
    Honors SAPHIRA_LOCAL_CAMERA_ENABLED. Always releases the camera handle.
    """
    if os.getenv("SAPHIRA_LOCAL_CAMERA_ENABLED", "false").lower() != "true":
        return DetectionResult(
            text_summary="Local camera capture is disabled.",
            detections=[],
        )

    model = get_detector()
    if model is None:
        return DetectionResult(
            text_summary="Object detector not available.",
            detections=[],
        )

    cap = cv2.VideoCapture(camera_index)
    try:
        if not cap.isOpened():
            logger.error("Unable to open camera index %s", camera_index)
            return DetectionResult(
                text_summary=f"Camera {camera_index} unavailable.",
                detections=[],
            )
        ret, frame = cap.read()
        if not ret or frame is None:
            return DetectionResult(
                text_summary="Failed to capture frame.",
                detections=[],
            )

        raw = model(frame, verbose=False)
        detections = decode_detections(raw, confidence_threshold)
        text = format_detections_as_text(detections)
        return DetectionResult(
            text_summary=text,
            detections=detections,
            frame_shape=list(frame.shape[:2]),
        )
    finally:
        cap.release()
