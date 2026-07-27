# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Matter / Home Assistant Connector for Saphira AI
# Primary path: Saphira → this connector → Home Assistant → Matter devices

import os
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("SaphiraMatterHA")


class MatterHomeAssistantConnector:
    """
    Controls Matter-compatible devices through Home Assistant.
    Uses the Home Assistant REST API (and optionally WebSocket later).
    """

    def __init__(self):
        self.base_url = os.getenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123").rstrip("/")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.token:
            return {"status": "error", "message": "HOME_ASSISTANT_TOKEN not set"}
        url = f"{self.base_url}{path}"
        try:
            r = requests.request(method, url, headers=self.headers, json=json, timeout=15)
            r.raise_for_status()
            return {"status": "success", "data": r.json() if r.content else {}}
        except Exception as e:
            logger.error(f"HA request failed: {e}")
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Device discovery
    # ------------------------------------------------------------------
    def list_states(self) -> Dict[str, Any]:
        """Return all entity states (lights, locks, climate, covers, etc.)."""
        return self._request("GET", "/api/states")

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/states/{entity_id}")

    # ------------------------------------------------------------------
    # Common Matter-mapped actions
    # ------------------------------------------------------------------
    def turn_on(self, entity_id: str, **kwargs) -> Dict[str, Any]:
        """Turn on a light, switch, or similar device."""
        payload = {"entity_id": entity_id, **kwargs}
        return self._request("POST", "/api/services/homeassistant/turn_on", json=payload)

    def turn_off(self, entity_id: str) -> Dict[str, Any]:
        payload = {"entity_id": entity_id}
        return self._request("POST", "/api/services/homeassistant/turn_off", json=payload)

    def toggle(self, entity_id: str) -> Dict[str, Any]:
        payload = {"entity_id": entity_id}
        return self._request("POST", "/api/services/homeassistant/toggle", json=payload)

    def set_brightness(self, entity_id: str, brightness_pct: int) -> Dict[str, Any]:
        """Set light brightness 0-100 (maps to Matter LevelControl)."""
        payload = {
            "entity_id": entity_id,
            "brightness_pct": max(0, min(100, brightness_pct)),
        }
        return self._request("POST", "/api/services/light/turn_on", json=payload)

    def set_temperature(self, entity_id: str, temperature: float) -> Dict[str, Any]:
        """Set thermostat target temperature (Matter Thermostat cluster)."""
        payload = {
            "entity_id": entity_id,
            "temperature": temperature,
        }
        return self._request("POST", "/api/services/climate/set_temperature", json=payload)

    def lock(self, entity_id: str) -> Dict[str, Any]:
        """Lock a door (Matter DoorLock cluster)."""
        payload = {"entity_id": entity_id}
        return self._request("POST", "/api/services/lock/lock", json=payload)

    def unlock(self, entity_id: str) -> Dict[str, Any]:
        payload = {"entity_id": entity_id}
        return self._request("POST", "/api/services/lock/unlock", json=payload)

    def set_cover_position(self, entity_id: str, position: int) -> Dict[str, Any]:
        """Set window covering / shade position 0-100."""
        payload = {
            "entity_id": entity_id,
            "position": max(0, min(100, position)),
        }
        return self._request("POST", "/api/services/cover/set_cover_position", json=payload)

    def call_service(self, domain: str, service: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic service caller for any HA / Matter-exposed entity."""
        return self._request("POST", f"/api/services/{domain}/{service}", json=data)

    # ------------------------------------------------------------------
    # High-level natural language helpers used by agents
    # ------------------------------------------------------------------
    def execute_intent(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map simple intents coming from Saphira / Agent Zero into HA calls.
        Examples:
          intent="turn_on", params={"entity_id": "light.living_room"}
          intent="set_brightness", params={"entity_id": "light.kitchen", "brightness_pct": 30}
          intent="lock", params={"entity_id": "lock.front_door"}
        """
        intent = intent.lower().strip()
        entity_id = params.get("entity_id", "")

        if intent in ("turn_on", "on"):
            return self.turn_on(entity_id, **{k: v for k, v in params.items() if k != "entity_id"})
        if intent in ("turn_off", "off"):
            return self.turn_off(entity_id)
        if intent == "toggle":
            return self.toggle(entity_id)
        if intent in ("set_brightness", "brightness", "dim"):
            return self.set_brightness(entity_id, int(params.get("brightness_pct", 50)))
        if intent in ("set_temperature", "temperature"):
            return self.set_temperature(entity_id, float(params.get("temperature", 72)))
        if intent == "lock":
            return self.lock(entity_id)
        if intent == "unlock":
            return self.unlock(entity_id)
        if intent in ("set_cover", "cover_position"):
            return self.set_cover_position(entity_id, int(params.get("position", 50)))

        return {"status": "error", "message": f"Unknown intent: {intent}"}


# Convenience singleton
matter_ha = MatterHomeAssistantConnector()
