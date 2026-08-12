"""Print controller for Saphira IoT routing."""

from __future__ import annotations

from typing import Any, Dict, Optional


class PrintController:
    """Handles print / 3D-print related intents."""

    def __init__(self) -> None:
        self._jobs: list[Dict[str, Any]] = []
        self._status: Dict[str, Any] = {
            "state": "idle",
            "progress": 0,
            "current_job": None,
        }

    def handle(self, intent: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        job = {"intent": intent, "payload": payload}
        self._jobs.append(job)
        self._status["current_job"] = job
        self._status["state"] = "running"
        return {"status": "ok", "job": job}

    def get_print_status(self) -> Dict[str, Any]:
        return dict(self._status)

    def jobs(self) -> list[Dict[str, Any]]:
        return list(self._jobs)
