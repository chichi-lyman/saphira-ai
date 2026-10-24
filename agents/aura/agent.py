# Copyright © 2026 Chelsea Megan Woods
"""
Aura — Perception agent for Saphira AI.

Owns multimodal perception (vision, face recognition, future audio cues).
Never exposes internal agent names to the user surface.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .face import FaceRecognitionService, FacePerceptionResult, decode_image_payload

logger = logging.getLogger("saphira.aura")


class AuraAgent:
    name = "aura"
    default_policy = "ALLOW"

    def __init__(self) -> None:
        self._face_service = FaceRecognitionService()

    def perceive(self, payload: dict) -> dict:
        """
        Main perception entry point.

        Supported payload shapes:
        - {"type": "face", "image_b64": "...", "known_faces": [...], ...}
        - {"type": "image", ...}  (generic vision, currently routes to face)
        - legacy plain dict (passed through)
        """
        ptype = (payload.get("type") or "").lower()

        if ptype in ("face", "face_recognition", "image"):
            return self._perceive_face(payload)

        # Fallback: echo for non-vision payloads (keeps existing callers working)
        return {
            "agent": self.name,
            "perception": payload,
            "status": "ok",
            "modality": "passthrough",
        }

    def enroll_face(
        self,
        image_payload: dict,
        label: str,
        consent_token: str,
    ) -> dict:
        """
        Extract an embedding for later storage by the memory layer.
        Requires an explicit consent_token (generated after user says "yes").
        """
        image_bytes = decode_image_payload(image_payload)
        if image_bytes is None:
            return {
                "agent": self.name,
                "status": "error",
                "message": "No valid image found in payload",
            }

        result = self._face_service.enroll(
            image_bytes,
            label=label,
            consent_token=consent_token,
        )
        result["agent"] = self.name
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _perceive_face(self, payload: dict) -> dict:
        image_bytes = decode_image_payload(payload)
        if image_bytes is None:
            return {
                "agent": self.name,
                "status": "error",
                "message": "No valid image (image_b64 / image_bytes) supplied",
                "modality": "face",
            }

        known = payload.get("known_faces") or []
        encodings: List[List[float]] = []
        labels: List[str] = []
        for entry in known:
            if isinstance(entry, dict) and "embedding" in entry and "label" in entry:
                encodings.append(entry["embedding"])
                labels.append(entry["label"])

        return_embeddings = bool(payload.get("return_embeddings", False))

        result: FacePerceptionResult = self._face_service.perceive(
            image_bytes,
            return_embeddings=return_embeddings,
            known_encodings=encodings or None,
            known_labels=labels or None,
        )

        out = result.to_dict()
        out["agent"] = self.name
        out["modality"] = "face"
        return out
