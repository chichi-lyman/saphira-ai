"""Matter / smart-home adapter with L1 safety for locks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Set

SECURITY_ACTIONS: Set[str] = {"unlock", "disarm", "open_garage", "disable_alarm"}

@dataclass
class DeviceCommand:
    device_id: str
    action: str
    params: Dict[str, Any]

class MatterBridge:
    def plan(self, command: DeviceCommand, confirmed: bool = False) -> Dict[str, Any]:
        action = command.action.lower()
        if action in SECURITY_ACTIONS and not confirmed:
            return {"status": "needs_confirmation", "level": "L1_confirm_first", "command": {"device_id": command.device_id, "action": action, "params": command.params}, "message": "Security-sensitive device action requires explicit confirmation."}
        return {"status": "planned", "level": "L2_supervised", "command": {"device_id": command.device_id, "action": action, "params": command.params}}

matter_bridge = MatterBridge()
