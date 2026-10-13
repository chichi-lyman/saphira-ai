# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Unit tests for vision object detection helpers."""

from __future__ import annotations

from unittest.mock import patch

from src.core.vision_detector import (
    Detection,
    DetectionResult,
    decode_detections,
    format_detections_as_text,
    process_camera_frame,
)


def test_format_detections_as_text_empty():
    assert format_detections_as_text([]) == "No objects detected above confidence threshold."


def test_format_detections_as_text_with_items():
    dets = [
        Detection(label="person", confidence=0.92, bbox=[10, 20, 100, 200]),
        Detection(label="cup", confidence=0.81, bbox=[50, 60, 80, 90]),
    ]
    text = format_detections_as_text(dets)
    assert "Detected 2 object(s)" in text
    assert "person (0.92)" in text
    assert "cup (0.81)" in text


def test_process_camera_frame_disabled(monkeypatch):
    monkeypatch.setenv("SAPHIRA_LOCAL_CAMERA_ENABLED", "false")
    result = process_camera_frame()
    assert isinstance(result, DetectionResult)
    assert result.detections == []
    assert "disabled" in result.text_summary.lower()


def test_decode_detections_empty():
    assert decode_detections(None) == []
    assert decode_detections([]) == []


@patch("src.core.vision_detector.get_detector")
@patch("src.core.vision_detector.cv2.VideoCapture")
def test_process_camera_frame_no_model(mock_cap, mock_get, monkeypatch):
    monkeypatch.setenv("SAPHIRA_LOCAL_CAMERA_ENABLED", "true")
    mock_get.return_value = None
    result = process_camera_frame()
    assert "not available" in result.text_summary.lower()
    assert result.detections == []
