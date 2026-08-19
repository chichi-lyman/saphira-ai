# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Local multimodal perception adapters.

Hardware access is opt-in. The server does not continuously capture camera or
microphone data without an explicit request from a connected node.
"""
from __future__ import annotations

import base64
import io
import os
from typing import Any


class SaphiraSensoryPerception:
    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate

    def capture_vision_frame(self) -> str:
        """Capture one local camera frame when explicitly enabled."""
        if os.getenv("SAPHIRA_LOCAL_CAMERA_ENABLED", "false").lower() != "true":
            return ""
        try:
            import cv2
        except ImportError:
            return ""
        cap = cv2.VideoCapture(0)
        try:
            ok, frame = cap.read()
            if not ok:
                return ""
            ok, buffer = cv2.imencode(".jpg", frame)
            return base64.b64encode(buffer).decode("ascii") if ok else ""
        finally:
            cap.release()

    def capture_audio_snippet(self, duration_seconds: float = 3.0) -> bytes:
        """Capture a short local audio sample when explicitly enabled."""
        if os.getenv("SAPHIRA_LOCAL_MIC_ENABLED", "false").lower() != "true":
            return b""
        try:
            import sounddevice as sd
        except ImportError:
            return b""
        import numpy as np
        frames = int(duration_seconds * self.sample_rate)
        recording = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()
        return np.asarray(recording).tobytes()

    @staticmethod
    def image_part(base64_jpeg: str) -> dict[str, Any] | None:
        if not base64_jpeg:
            return None
        return {"mime_type": "image/jpeg", "data": base64.b64decode(base64_jpeg)}
