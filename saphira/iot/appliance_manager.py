"""Appliance manager stub for Saphira IoT routing."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ApplianceManager:
    """Controls household appliances via intent routing."""

    def __init__(self) -> None:
        self._state: Dict[str, Any] = {}

    def handle(self, intent: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        self._state[intent] = payload
        return {"status": "ok", "intent": intent, "payload": payload}

    def status(self) -> Dict[str, Any]:
        return dict(self._state)
