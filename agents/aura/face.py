# Copyright © 2026 Chelsea Megan Woods
# Saphira AI — Aura Perception: Face Recognition
# Privacy-first: embeddings only stored after explicit user consent.
# Prefer on-device inference (MediaPipe / ML Kit). Server path is opt-in.

from __future__ import annotations

import base64
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("saphira.aura.face")

# ---------------------------------------------------------------------------
# Optional heavy backends (graceful degradation)
# ---------------------------------------------------------------------------
_HAS_MEDIAPIPE = False
_HAS_FACE_RECOGNITION = False
_HAS_OPENCV = False
_HAS_DEEPFACE = False

try:
    import cv2

    _HAS_OPENCV = True
except ImportError:
    cv2 = None  # type: ignore

try:
    import mediapipe as mp

    _HAS_MEDIAPIPE = True
except ImportError:
    mp = None  # type: ignore

try:
    import face_recognition

    _HAS_FACE_RECOGNITION = True
except ImportError:
    face_recognition = None  # type: ignore

try:
    from deepface import DeepFace

    _HAS_DEEPFACE = True
except ImportError:
    DeepFace = None  # type: ignore


@dataclass
class FaceMatch:
    label: str
    distance: float
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]] = None  # (top, right, bottom, left)


@dataclass
class FacePerceptionResult:
    faces_detected: int = 0
    matches: List[FaceMatch] = field(default_factory=list)
    embeddings: List[List[float]] = field(default_factory=list)  # only returned when requested
    raw_locations: List[Tuple[int, int, int, int]] = field(default_factory=list)
    backend: str = "none"
    status: str = "ok"
    message: str = ""
    requires_consent: bool = False  # true when new face seen and no match

    def to_dict(self) -> Dict[str, Any]:
        return {
            "faces_detected": self.faces_detected,
            "matches": [
                {
                    "label": m.label,
                    "distance": round(m.distance, 4),
                    "confidence": round(m.confidence, 4),
                    "bbox": m.bbox,
                }
                for m in self.matches
            ],
            "embeddings_count": len(self.embeddings),
            "raw_locations": self.raw_locations,
            "backend": self.backend,
            "status": self.status,
            "message": self.message,
            "requires_consent": self.requires_consent,
        }


class FaceRecognitionService:
    """
    Privacy-first face recognition service used by Aura.

    Design rules:
    - Never persist an embedding unless the caller explicitly requests enrollment
      after user consent.
    - Prefer local backends (MediaPipe + simple matching, or face_recognition).
    - Known faces are supplied by the memory layer (NovaAethrea) only after
      the user has approved them.
    """

    # Default threshold for face_recognition / dlib (lower = stricter)
    DEFAULT_TOLERANCE = 0.55

    def __init__(self, tolerance: float = DEFAULT_TOLERANCE):
        self.tolerance = tolerance
        self._known_encodings: List[np.ndarray] = []
        self._known_labels: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_known_faces(
        self,
        encodings: List[List[float]],
        labels: List[str],
    ) -> None:
        """Load already-consented faces from the memory store."""
        if len(encodings) != len(labels):
            raise ValueError("encodings and labels must have the same length")
        self._known_encodings = [np.asarray(e, dtype=np.float64) for e in encodings]
        self._known_labels = list(labels)
        logger.info("Loaded %d known faces", len(labels))

    def enroll(
        self,
        image_bytes: bytes,
        label: str,
        *,
        consent_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract embedding for a new face. Does **not** persist it.
        Persistence is the responsibility of the memory layer after
        the user has given explicit consent.
        """
        if not consent_token:
            return {
                "status": "consent_required",
                "message": "Explicit consent_token required before enrollment.",
            }

        encoding, location, backend = self._extract_encoding(image_bytes)
        if encoding is None:
            return {
                "status": "no_face",
                "message": "No face detected in the provided image.",
                "backend": backend,
            }

        # Return the embedding so the memory layer can store it under the label
        return {
            "status": "ok",
            "label": label,
            "embedding": encoding.tolist(),
            "location": location,
            "backend": backend,
            "embedding_sha256": hashlib.sha256(encoding.tobytes()).hexdigest()[:16],
            "message": "Embedding extracted. Store only after user confirmation.",
        }

    def perceive(
        self,
        image_bytes: bytes,
        *,
        return_embeddings: bool = False,
        known_encodings: Optional[List[List[float]]] = None,
        known_labels: Optional[List[str]] = None,
    ) -> FacePerceptionResult:
        """
        Main perception entry point used by AuraAgent.

        If known_encodings/labels are supplied they override the in-memory set
        (useful when the memory layer injects the current user roster).
        """
        if known_encodings is not None and known_labels is not None:
            self.load_known_faces(known_encodings, known_labels)

        encoding, location, backend = self._extract_encoding(image_bytes)

        if encoding is None:
            return FacePerceptionResult(
                faces_detected=0,
                backend=backend,
                status="no_face",
                message="No face detected",
            )

        result = FacePerceptionResult(
            faces_detected=1,
            raw_locations=[location] if location else [],
            backend=backend,
            status="ok",
        )

        if return_embeddings:
            result.embeddings = [encoding.tolist()]

        if not self._known_encodings:
            result.requires_consent = True
            result.message = "Unknown face. User consent required to enroll."
            return result

        # Match against known faces
        distances = [
            float(np.linalg.norm(encoding - known))
            for known in self._known_encodings
        ]
        best_idx = int(np.argmin(distances))
        best_dist = distances[best_idx]

        if best_dist <= self.tolerance:
            confidence = max(0.0, 1.0 - (best_dist / self.tolerance))
            result.matches.append(
                FaceMatch(
                    label=self._known_labels[best_idx],
                    distance=best_dist,
                    confidence=confidence,
                    bbox=location,
                )
            )
            result.message = f"Recognized as {self._known_labels[best_idx]}"
        else:
            result.requires_consent = True
            result.message = "Face detected but no confident match."

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_encoding(
        self, image_bytes: bytes
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
        """Try backends in order of preference."""
        # 1. face_recognition (dlib) — highest quality when available
        if _HAS_FACE_RECOGNITION:
            try:
                return self._extract_with_face_recognition(image_bytes)
            except Exception as exc:
                logger.warning("face_recognition backend failed: %s", exc)

        # 2. DeepFace (multiple model backends)
        if _HAS_DEEPFACE:
            try:
                return self._extract_with_deepface(image_bytes)
            except Exception as exc:
                logger.warning("DeepFace backend failed: %s", exc)

        # 3. MediaPipe (lightweight, good for on-device style)
        if _HAS_MEDIAPIPE and _HAS_OPENCV:
            try:
                return self._extract_with_mediapipe(image_bytes)
            except Exception as exc:
                logger.warning("MediaPipe backend failed: %s", exc)

        # 4. OpenCV Haar cascade (detection only, no real embedding)
        if _HAS_OPENCV:
            try:
                return self._extract_with_opencv_haar(image_bytes)
            except Exception as exc:
                logger.warning("OpenCV Haar backend failed: %s", exc)

        return None, None, "none"

    def _bytes_to_rgb(self, image_bytes: bytes) -> np.ndarray:
        if not _HAS_OPENCV:
            raise RuntimeError("OpenCV is required to decode image bytes")
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError("Could not decode image bytes")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    def _extract_with_face_recognition(
        self, image_bytes: bytes
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
        assert face_recognition is not None
        rgb = self._bytes_to_rgb(image_bytes)
        locations = face_recognition.face_locations(rgb, model="hog")
        if not locations:
            return None, None, "face_recognition"
        encodings = face_recognition.face_encodings(rgb, locations)
        if not encodings:
            return None, None, "face_recognition"
        # Return first face only for simplicity (multi-face can be added later)
        top, right, bottom, left = locations[0]
        return encodings[0], (top, right, bottom, left), "face_recognition"

    def _extract_with_deepface(
        self, image_bytes: bytes
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
        assert DeepFace is not None and _HAS_OPENCV
        rgb = self._bytes_to_rgb(image_bytes)
        # DeepFace expects BGR or path; we pass numpy
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        reps = DeepFace.represent(
            bgr,
            model_name="Facenet",
            enforce_detection=True,
            detector_backend="opencv",
        )
        if not reps:
            return None, None, "deepface"
        emb = np.asarray(reps[0]["embedding"], dtype=np.float64)
        # DeepFace does not always return clean bbox in the same format
        return emb, None, "deepface"

    def _extract_with_mediapipe(
        self, image_bytes: bytes
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
        """Detection + simple landmark-based embedding (not production SOTA)."""
        assert mp is not None and _HAS_OPENCV
        rgb = self._bytes_to_rgb(image_bytes)
        h, w, _ = rgb.shape

        with mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        ) as detector:
            results = detector.process(rgb)
            if not results.detections:
                return None, None, "mediapipe"

            det = results.detections[0]
            bbox = det.location_data.relative_bounding_box
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)
            location = (y, x + bw, y + bh, x)  # top, right, bottom, left

            # Very lightweight "embedding": flattened normalized landmarks
            # (replace with a real FaceNet/ArcFace ONNX model for production)
            face_crop = rgb[max(0, y) : y + bh, max(0, x) : x + bw]
            if face_crop.size == 0:
                return None, location, "mediapipe"
            face_resized = cv2.resize(face_crop, (64, 64)).astype(np.float32) / 255.0
            emb = face_resized.flatten()
            # L2 normalize
            emb = emb / (np.linalg.norm(emb) + 1e-8)
            return emb, location, "mediapipe"

    def _extract_with_opencv_haar(
        self, image_bytes: bytes
    ) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]], str]:
        """Detection only — returns a dummy embedding so the pipeline still works."""
        assert _HAS_OPENCV
        rgb = self._bytes_to_rgb(image_bytes)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) == 0:
            return None, None, "opencv_haar"
        x, y, w, h = faces[0]
        location = (y, x + w, y + h, x)
        # Dummy embedding (zeros) — signals that real recognition is unavailable
        emb = np.zeros(128, dtype=np.float64)
        return emb, location, "opencv_haar"


def decode_image_payload(payload: Dict[str, Any]) -> Optional[bytes]:
    """Accept common image payload shapes used by mobile / web clients."""
    if "image_b64" in payload:
        return base64.b64decode(payload["image_b64"])
    if "image_bytes" in payload:
        data = payload["image_bytes"]
        if isinstance(data, str):
            return base64.b64decode(data)
        return bytes(data)
    if "image_url" in payload:
        # Caller should have already fetched; we do not pull remote images
        # to keep the privacy boundary clean.
        logger.warning("image_url provided but remote fetch is disabled by policy")
    return None
