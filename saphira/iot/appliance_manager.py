"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - Media Controller Module
"""

import logging
from typing import Dict, Any, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraMediaController")

class MediaController:
    def __init__(self, default_device: str = "living_room_tv"):
        self.default_device = default_device
        self.active_sessions: Dict[str, Any] = {}

    async def power_device(self, device_id: Optional[str] = None, state: str = "on") -> Dict[str, Any]:
        target = device_id or self.default_device
        logger.info(f"Turning {state} media device: {target}")
        return {"device": target, "status": "success", "power": state}

    async def play_media(self, media_title: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_device
        logger.info(f"Playing '{media_title}' on {target}")
        self.active_sessions[target] = {"current_media": media_title, "state": "playing"}
        return {
            "device": target,
            "status": "success",
            "action": "play",
            "media": media_title,
            "message": f"Now playing {media_title} on your display, Chelsea Megan Woods."
        }

    async def change_channel(self, channel: Union[str, int], device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_device
        logger.info(f"Changing channel to {channel} on {target}")
        return {
            "device": target,
            "status": "success",
            "channel": channel,
            "message": f"Switched channel to {channel}."
        }

    async def get_what_is_playing(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_device
        current = self.active_sessions.get(target, {"current_media": "Nothing currently active", "state": "idle"})
        logger.info(f"Checking status for {target}: {current}")
        return {
            "device": target,
            "status": "success",
            "playback_info": current
        }
