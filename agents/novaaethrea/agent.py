# Copyright © 2026 Chelsea Megan Woods
"""
NovaAethrea — Memory agent for Saphira AI.

Owns explicit fact ledgers, preferences, scenes, history, and consented
face embeddings. Never stores face data without a consent token.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("saphira.novaaethrea")


class NovaAethreaAgent:
    name = "novaaethrea"
    default_policy = "ALLOW"

    def __init__(self, memory_store=None) -> None:
        # Lazy import avoids circular deps at package load time
        if memory_store is None:
            try:
                from src.memory.persistent_store import persistent_memory

                self._store = persistent_memory
            except Exception:
                self._store = None
        else:
            self._store = memory_store

    def remember(self, key: str, value: dict) -> dict:
        """Generic key/value remember (legacy + general facts)."""
        if self._store is not None:
            self._store.set_fact(key, value)
        return {"agent": self.name, "stored": key, "value": value}

    # ------------------------------------------------------------------
    # Face memory (consent-gated)
    # ------------------------------------------------------------------

    def store_face(
        self,
        label: str,
        embedding: List[float],
        *,
        consent_token: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Persist a face embedding only when a consent_token is present.
        Called after Aura.enroll_face and an explicit user "yes".
        """
        if not consent_token:
            return {
                "agent": self.name,
                "status": "consent_required",
                "message": "Cannot store face without explicit consent_token",
            }

        if self._store is None:
            return {
                "agent": self.name,
                "status": "error",
                "message": "Memory store unavailable",
            }

        record = {
            "label": label,
            "embedding": embedding,
            "consent_token": consent_token,
            "metadata": metadata or {},
        }
        self._store.set_face(label, record)
        logger.info("Stored consented face embedding for label=%s", label)
        return {
            "agent": self.name,
            "status": "ok",
            "label": label,
            "message": f"Remembered face as '{label}'",
        }

    def list_faces(self) -> dict:
        if self._store is None:
            return {"agent": self.name, "faces": [], "status": "error"}
        faces = self._store.list_faces()
        # Never return raw embeddings to casual callers unless asked
        safe = [{"label": f["label"], "metadata": f.get("metadata", {})} for f in faces]
        return {"agent": self.name, "faces": safe, "status": "ok"}

    def get_known_faces_for_perception(self) -> List[Dict[str, Any]]:
        """Return label + embedding pairs suitable for Aura.perceive."""
        if self._store is None:
            return []
        return [
            {"label": f["label"], "embedding": f["embedding"]}
            for f in self._store.list_faces()
            if "embedding" in f
        ]

    def forget_face(self, label: str) -> dict:
        if self._store is None:
            return {"agent": self.name, "status": "error"}
        removed = self._store.delete_face(label)
        return {
            "agent": self.name,
            "status": "ok" if removed else "not_found",
            "label": label,
        }
