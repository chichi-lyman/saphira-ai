# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Goal-driven perception -> reasoning -> action -> verification loop."""
from __future__ import annotations

import json
import os
from typing import Any

from google import genai
from google.genai import types

from src.core.perception import SaphiraSensoryPerception


class SaphiraAwarenessEngine:
    """Bounded multimodal loop. External actions are returned as proposals.

    Consequential execution must be delegated to Saphira's existing governance
    kernel rather than allowing model-generated strings to execute directly.
    """

    def __init__(self, google_gemini_key: str | None = None) -> None:
        self.client = genai.Client(api_key=google_gemini_key or os.getenv("GEMINI_API_KEY"))
        self.sensors = SaphiraSensoryPerception()

    async def execute_goal_with_awareness(self, target_goal: str, max_loops: int = 5) -> dict[str, Any]:
        max_loops = max(1, min(max_loops, 10))
        history: list[dict[str, Any]] = []

        for loop_count in range(max_loops):
            image = self.sensors.capture_vision_frame()
            prompt = (
                f'Goal: {target_goal}\n'
                "Evaluate the supplied scene. Return ONLY JSON with keys: "
                'status (WORKING|COMPLETED|BLOCKED), next_action, issue_detected. '
                "next_action must be a proposed action, never an executable shell command."
            )
            parts: list[Any] = [prompt]
            image_part = self.sensors.image_part(image)
            if image_part:
                parts.append(image_part)

            response = await self.client.aio.models.generate_content(
                model=os.getenv("SAPHIRA_AWARENESS_MODEL", "gemini-2.5-flash"),
                contents=parts,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            try:
                state = json.loads(response.text or "{}")
            except json.JSONDecodeError:
                state = {"status": "BLOCKED", "next_action": "", "issue_detected": "Invalid model JSON"}

            history.append({"iteration": loop_count + 1, "evaluation": state})
            if state.get("status") == "COMPLETED":
                return {"status": "SUCCESS", "history": history}
            if state.get("status") == "BLOCKED":
                return {"status": "BLOCKED", "history": history}

            # Intentionally no subprocess/browser execution here. The proposed
            # action must pass through the governance/action adapter first.

        return {"status": "TIMEOUT", "history": history}
