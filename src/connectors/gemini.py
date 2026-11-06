# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import os
from typing import Dict, Any, Optional


class GeminiConnector:
    """
    Lightweight Gemini connector supporting both:
    - Vertex AI (GOOGLE_CLOUD_PROJECT + VERTEX_LOCATION)
    - Gemini Developer API (GEMINI_API_KEY)

    Prefer Vertex in production. Falls back to API key when project is unset.
    """

    def __init__(self):
        self.api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        self.project = (os.getenv("GOOGLE_CLOUD_PROJECT") or "").strip()
        self.location = (os.getenv("VERTEX_LOCATION") or "us-central1").strip()
        self.vertex_enabled = (os.getenv("VERTEX_ENABLED", "true") or "true").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )

    def _use_vertex(self) -> bool:
        return bool(self.vertex_enabled and self.project)

    def generate(self, prompt: str, model: str = "gemini-2.5-flash") -> Dict[str, Any]:
        if not self._use_vertex() and not self.api_key:
            return {
                "status": "error",
                "message": "Set GOOGLE_CLOUD_PROJECT (Vertex) or GEMINI_API_KEY",
            }
        try:
            from google import genai

            if self._use_vertex():
                client = genai.Client(
                    vertexai=True,
                    project=self.project,
                    location=self.location,
                )
                backend = "vertex"
            else:
                client = genai.Client(api_key=self.api_key)
                backend = "developer"

            res = client.models.generate_content(model=model, contents=prompt)
            return {
                "status": "success",
                "text": getattr(res, "text", None) or "",
                "backend": backend,
                "model": model,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
