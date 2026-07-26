"""
Saphira AI - Appliance Manager Module
Architected and Built by Chelsea Megan Woods
"""

import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraApplianceManager")

class ApplianceManager:
    def __init__(self, default_vacuum: str = "robot_vacuum_1"):
        self.default_vacuum = default_vacuum

    async def control_vacuum(self, action: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        target = device_id or self.default_vacuum
        logger.info(f"Vacuum action '{action}' requested for {target}")
        
        valid_actions = ["start", "stop", "dock", "pause"]
        if action.lower() not in valid_actions:
            return {"status": "error", "message": f"Invalid vacuum action. Choose from: {valid_actions}"}
            
        return {
            "device": target,
            "status": "success",
            "action": action,
            "message": f"Robot vacuum {target} has executed: {action}, Chelsea."
        }

    async def control_appliance(self, appliance_name: str, state: str) -> Dict[str, Any]:
        logger.info(f"Setting appliance {appliance_name} to {state}")
        return {
            "appliance": appliance_name,
            "status": "success",
            "state": state,
            "message": f"Appliance {appliance_name} is now {state}."
        }
