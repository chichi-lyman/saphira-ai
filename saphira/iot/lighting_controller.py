"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - Lighting Controller Module
Purpose: Manages Bluetooth and Wi-Fi smart bulbs, color adjustments, brightness, and power states.
"""

import logging
from typing import Dict, Any, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraLightingController")

class LightingController:
    def __init__(self, default_light: str = "color_bulb_1"):
        self.default_light = default_light

    async def power_light(self, device_id: Optional[str] = None, state: str = "on") -> Dict[str, Any]:
        target = device_id or self.default_light
        logger.info(f"Turning light {state} for: {target}")
        return {
            "device": target, 
            "status": "success", 
            "power": state,
            "message": f"Light {target} is now switched {state}, Chelsea Megan Woods."
        }

    async def set_color(self, color: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_light
        logger.info(f"Setting color of {target} to {color}")
        return {
            "device": target,
            "status": "success",
            "color": color,
            "message": f"Lighting color changed to {color}."
        }

    async def set_brightness(self, level: Union[int, str], device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_light
        logger.info(f"Setting brightness of {target} to {level}%")
        return {
            "device": target,
            "status": "success",
            "brightness": level,
            "message": f"Brightness adjusted to {level}%."
        }


