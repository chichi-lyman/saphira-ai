# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Matter / Home Assistant Connector for Saphira AI
# Expanded: more clusters + WebSocket live-state support

import os
import json
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
import requests

logger = logging.getLogger("SaphiraMatterHA")

try:
    import websocket  # websocket-client
    HAS_WS = True
except ImportError:
    HAS_WS = False


class MatterHomeAssistantConnector:
    """
    Controls Matter-compatible devices through Home Assistant.
    REST for commands + optional WebSocket for live state.
    """

    def __init__(self):
        self.base_url = os.getenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123").rstrip("/")
        self.token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self._ws = None
        self._ws_id = 1
        self._state_cache: Dict[str, Any] = {}
        self._listeners: List[Callable] = []
        self._ws_thread = None

    # ------------------------------------------------------------------
    # REST helpers
    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, json_body: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.token:
            return {"status": "error", "message": "HOME_ASSISTANT_TOKEN not set"}
        url = f"{self.base_url}{path}"
        try:
            r = requests.request(method, url, headers=self.headers, json=json_body, timeout=15)
            r.raise_for_status()
            return {"status": "success", "data": r.json() if r.content else {}}
        except Exception as e:
            logger.error(f"HA request failed: {e}")
            return {"status": "error", "message": str(e)}

    def list_states(self) -> Dict[str, Any]:
        return self._request("GET", "/api/states")

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/states/{entity_id}")

    def call_service(self, domain: str, service: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", f"/api/services/{domain}/{service}", json_body=data)

    # ------------------------------------------------------------------
    # Core device actions
    # ------------------------------------------------------------------
    def turn_on(self, entity_id: str, **kwargs) -> Dict[str, Any]:
        return self.call_service("homeassistant", "turn_on", {"entity_id": entity_id, **kwargs})

    def turn_off(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("homeassistant", "turn_off", {"entity_id": entity_id})

    def toggle(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("homeassistant", "toggle", {"entity_id": entity_id})

    def set_brightness(self, entity_id: str, brightness_pct: int) -> Dict[str, Any]:
        return self.call_service("light", "turn_on", {
            "entity_id": entity_id,
            "brightness_pct": max(0, min(100, brightness_pct)),
        })

    def set_color(self, entity_id: str, rgb: Optional[List[int]] = None,
                  kelvin: Optional[int] = None, hs: Optional[List[float]] = None) -> Dict[str, Any]:
        """ColorControl cluster via HA light service."""
        payload: Dict[str, Any] = {"entity_id": entity_id}
        if rgb:
            payload["rgb_color"] = rgb
        if kelvin:
            payload["color_temp_kelvin"] = kelvin
        if hs:
            payload["hs_color"] = hs
        return self.call_service("light", "turn_on", payload)

    def set_temperature(self, entity_id: str, temperature: float) -> Dict[str, Any]:
        return self.call_service("climate", "set_temperature", {
            "entity_id": entity_id,
            "temperature": temperature,
        })

    def set_hvac_mode(self, entity_id: str, mode: str) -> Dict[str, Any]:
        """heat / cool / heat_cool / off / auto / fan_only / dry"""
        return self.call_service("climate", "set_hvac_mode", {
            "entity_id": entity_id,
            "hvac_mode": mode,
        })

    def set_fan_mode(self, entity_id: str, fan_mode: str) -> Dict[str, Any]:
        return self.call_service("climate", "set_fan_mode", {
            "entity_id": entity_id,
            "fan_mode": fan_mode,
        })

    def fan_set_percentage(self, entity_id: str, percentage: int) -> Dict[str, Any]:
        return self.call_service("fan", "set_percentage", {
            "entity_id": entity_id,
            "percentage": max(0, min(100, percentage)),
        })

    def fan_set_preset(self, entity_id: str, preset: str) -> Dict[str, Any]:
        return self.call_service("fan", "set_preset_mode", {
            "entity_id": entity_id,
            "preset_mode": preset,
        })

    def lock(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("lock", "lock", {"entity_id": entity_id})

    def unlock(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("lock", "unlock", {"entity_id": entity_id})

    def set_cover_position(self, entity_id: str, position: int) -> Dict[str, Any]:
        return self.call_service("cover", "set_cover_position", {
            "entity_id": entity_id,
            "position": max(0, min(100, position)),
        })

    def open_cover(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("cover", "open_cover", {"entity_id": entity_id})

    def close_cover(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("cover", "close_cover", {"entity_id": entity_id})

    def media_play(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("media_player", "media_play", {"entity_id": entity_id})

    def media_pause(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("media_player", "media_pause", {"entity_id": entity_id})

    def media_stop(self, entity_id: str) -> Dict[str, Any]:
        return self.call_service("media_player", "media_stop", {"entity_id": entity_id})

    def media_set_volume(self, entity_id: str, volume: float) -> Dict[str, Any]:
        return self.call_service("media_player", "volume_set", {
            "entity_id": entity_id,
            "volume_level": max(0.0, min(1.0, volume)),
        })

    def activate_ha_scene(self, entity_id: str) -> Dict[str, Any]:
        """Activate a Home Assistant scene entity."""
        return self.call_service("scene", "turn_on", {"entity_id": entity_id})

    # ------------------------------------------------------------------
    # High-level intent router used by Agent Zero
    # ------------------------------------------------------------------
    def execute_intent(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        intent = intent.lower().strip()
        entity_id = params.get("entity_id", "")

        handlers = {
            "turn_on": lambda: self.turn_on(entity_id, **{k: v for k, v in params.items() if k != "entity_id"}),
            "on": lambda: self.turn_on(entity_id),
            "turn_off": lambda: self.turn_off(entity_id),
            "off": lambda: self.turn_off(entity_id),
            "toggle": lambda: self.toggle(entity_id),
            "set_brightness": lambda: self.set_brightness(entity_id, int(params.get("brightness_pct", 50))),
            "brightness": lambda: self.set_brightness(entity_id, int(params.get("brightness_pct", 50))),
            "dim": lambda: self.set_brightness(entity_id, int(params.get("brightness_pct", 30))),
            "set_color": lambda: self.set_color(
                entity_id,
                rgb=params.get("rgb"),
                kelvin=params.get("kelvin"),
                hs=params.get("hs"),
            ),
            "set_temperature": lambda: self.set_temperature(entity_id, float(params.get("temperature", 72))),
            "temperature": lambda: self.set_temperature(entity_id, float(params.get("temperature", 72))),
            "set_hvac_mode": lambda: self.set_hvac_mode(entity_id, params.get("mode", "auto")),
            "set_fan_mode": lambda: self.set_fan_mode(entity_id, params.get("fan_mode", "auto")),
            "fan_percentage": lambda: self.fan_set_percentage(entity_id, int(params.get("percentage", 50))),
            "fan_preset": lambda: self.fan_set_preset(entity_id, params.get("preset", "auto")),
            "lock": lambda: self.lock(entity_id),
            "unlock": lambda: self.unlock(entity_id),
            "set_cover": lambda: self.set_cover_position(entity_id, int(params.get("position", 50))),
            "cover_position": lambda: self.set_cover_position(entity_id, int(params.get("position", 50))),
            "open_cover": lambda: self.open_cover(entity_id),
            "close_cover": lambda: self.close_cover(entity_id),
            "media_play": lambda: self.media_play(entity_id),
            "media_pause": lambda: self.media_pause(entity_id),
            "media_stop": lambda: self.media_stop(entity_id),
            "media_volume": lambda: self.media_set_volume(entity_id, float(params.get("volume", 0.5))),
            "activate_scene": lambda: self.activate_ha_scene(entity_id),
        }

        handler = handlers.get(intent)
        if not handler:
            return {"status": "error", "message": f"Unknown intent: {intent}"}
        return handler()

    # ------------------------------------------------------------------
    # WebSocket live state
    # ------------------------------------------------------------------
    def add_state_listener(self, callback: Callable):
        self._listeners.append(callback)

    def get_cached_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self._state_cache.get(entity_id)

    def start_websocket(self):
        """Start background WebSocket for live state updates."""
        if not HAS_WS:
            logger.warning("websocket-client not installed; live state disabled")
            return {"status": "error", "message": "websocket-client not installed"}
        if not self.token:
            return {"status": "error", "message": "HOME_ASSISTANT_TOKEN not set"}

        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"

        def on_message(ws, message):
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "auth_required":
                    ws.send(json.dumps({"type": "auth", "access_token": self.token}))
                elif msg_type == "auth_ok":
                    # Subscribe to state changes
                    self._ws_id += 1
                    ws.send(json.dumps({
                        "id": self._ws_id,
                        "type": "subscribe_events",
                        "event_type": "state_changed",
                    }))
                    logger.info("HA WebSocket authenticated and subscribed")
                elif msg_type == "event":
                    event = data.get("event", {})
                    if event.get("event_type") == "state_changed":
                        new_state = event.get("data", {}).get("new_state")
                        if new_state and new_state.get("entity_id"):
                            eid = new_state["entity_id"]
                            self._state_cache[eid] = new_state
                            for cb in self._listeners:
                                try:
                                    cb(eid, new_state)
                                except Exception as e:
                                    logger.error(f"Listener error: {e}")
            except Exception as e:
                logger.error(f"WS message error: {e}")

        def on_error(ws, error):
            logger.error(f"HA WebSocket error: {error}")

        def on_close(ws, close_status, close_msg):
            logger.warning("HA WebSocket closed")

        def run():
            self._ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            self._ws.run_forever()

        self._ws_thread = threading.Thread(target=run, daemon=True)
        self._ws_thread.start()
        return {"status": "started", "message": "WebSocket live state started"}

    def stop_websocket(self):
        if self._ws:
            self._ws.close()
            self._ws = None
        return {"status": "stopped"}


# Singleton
matter_ha = MatterHomeAssistantConnector()
