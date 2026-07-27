# Offline Mode for Saphira AI
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("SaphiraOffline")

class OfflineModeManager:
    """
    Detects connectivity and routes requests to local-only capabilities
    when the network is unavailable or intentionally disabled.
    """

    def __init__(self):
        self.force_offline = False
        self._is_online = True

    def set_force_offline(self, value: bool):
        self.force_offline = value
        logger.info(f"Force offline set to {value}")

    def check_connectivity(self) -> bool:
        """In production this would ping a lightweight endpoint or use OS APIs."""
        if self.force_offline:
            self._is_online = False
            return False
        # Placeholder – assume online unless forced offline
        self._is_online = True
        return True

    def route_request(self, intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        online = self.check_connectivity()
        if online:
            return {"mode": "hybrid", "intent": intent, "payload": payload}

        # Offline-capable intents
        offline_safe = {
            "boundary_coach", "lifestyle_orchestrator",
            "relationship", "admin_resolver", "local_timer", "device_toggle"
        }

        if intent in offline_safe:
            return {
                "mode": "offline",
                "intent": intent,
                "payload": payload,
                "note": "Using local SLM + cached memory only"
            }

        return {
            "mode": "offline_limited",
            "intent": intent,
            "message": "This request needs cloud reasoning. I can still help with local tasks while offline."
        }
