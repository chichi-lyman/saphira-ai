# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Agent Zero — System Orchestrator & Execution Engine
# Now includes Matter / Home Assistant smart-home execution

from typing import Dict, Any
from src.connectors.matter_home_assistant import matter_ha
import logging

logger = logging.getLogger("AgentZero")


class AgentZero:
    """Hands-on execution engine. Runs system commands and smart-home actions."""

    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "")
        params = payload.get("params", {})

        # Smart-home / Matter path
        if action in (
            "turn_on", "turn_off", "toggle", "set_brightness",
            "set_temperature", "lock", "unlock", "set_cover", "matter"
        ):
            result = self.matter.execute_intent(action, params)
            return {
                "status": result.get("status", "unknown"),
                "agent": "agent_zero",
                "action": action,
                "result": result,
            }

        # Generic system / script execution placeholder
        return {
            "status": "accepted",
            "agent": "agent_zero",
            "message": f"Execution request received: {action}",
            "params": params,
        }
