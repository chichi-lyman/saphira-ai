# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Device Executor with Strict Timeout Protection
# Prevents smart home command loops and device bottlenecks

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("SaphiraDeviceExecutor")

# Global timeout for all device commands (2.5 seconds)
DEVICE_COMMAND_TIMEOUT = 2.5

# Maximum retries per device (prevent infinite loops)
MAX_DEVICE_RETRIES = 2


class DeviceExecutorWithTimeout:
    """Execute IoT device commands with strict timeout protection."""

    def __init__(self, timeout_seconds: float = DEVICE_COMMAND_TIMEOUT, max_retries: int = MAX_DEVICE_RETRIES):
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.command_history: Dict[str, Any] = {}

    async def execute_with_timeout(
        self,
        device_command: Dict[str, Any],
        executor_func: Any,
    ) -> Dict[str, Any]:
        """
        Execute device command with timeout protection.
        
        Args:
            device_command: Dict with action, params, entity_id
            executor_func: Async function that executes the command (e.g., Agent Zero)
            
        Returns:
            Dict with status, elapsed_ms, result/error
        """
        start_time = datetime.now()
        command_id = device_command.get("id") or str(hash(str(device_command)))
        action = device_command.get("action", "unknown")
        entity_id = device_command.get("params", {}).get("entity_id", "unknown")

        try:
            # Attempt execution with strict timeout
            logger.info(f"[{command_id}] Executing {action} on {entity_id}")
            
            result = await asyncio.wait_for(
                executor_func(device_command),
                timeout=self.timeout
            )
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"[{command_id}] Success in {elapsed_ms:.0f}ms")
            
            self.command_history[command_id] = {
                "status": "success",
                "action": action,
                "entity": entity_id,
                "elapsed_ms": elapsed_ms,
                "timestamp": start_time
            }
            
            return {
                "status": "success",
                "action": action,
                "entity_id": entity_id,
                "result": result,
                "elapsed_ms": elapsed_ms,
                "command_id": command_id,
                "message": f"Device command executed successfully in {elapsed_ms:.0f}ms"
            }

        except asyncio.TimeoutError:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.warning(
                f"[{command_id}] TIMEOUT after {self.timeout}s: {action} on {entity_id}"
            )
            
            self.command_history[command_id] = {
                "status": "timeout",
                "action": action,
                "entity": entity_id,
                "elapsed_ms": elapsed_ms,
                "timestamp": start_time,
                "reason": "Device did not respond within timeout window"
            }
            
            # Return timeout error without crashing
            return {
                "status": "timeout",
                "action": action,
                "entity_id": entity_id,
                "error": f"Device did not respond within {self.timeout}s",
                "elapsed_ms": elapsed_ms,
                "command_id": command_id,
                "message": f"Device timeout: {entity_id} may be offline or unresponsive. Command aborted."
            }

        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(
                f"[{command_id}] ERROR executing {action} on {entity_id}: {str(e)}"
            )
            
            self.command_history[command_id] = {
                "status": "error",
                "action": action,
                "entity": entity_id,
                "elapsed_ms": elapsed_ms,
                "timestamp": start_time,
                "error": str(e)
            }
            
            return {
                "status": "error",
                "action": action,
                "entity_id": entity_id,
                "error": str(e),
                "elapsed_ms": elapsed_ms,
                "command_id": command_id,
                "message": f"Device command failed: {str(e)}"
            }

    async def execute_batch_with_timeout(
        self,
        device_commands: list,
        executor_func: Any,
    ) -> Dict[str, Any]:
        """
        Execute multiple device commands in parallel (not sequentially).
        If one device times out, others continue.
        
        Args:
            device_commands: List of device command dicts
            executor_func: Async function that executes commands
            
        Returns:
            Dict with results from all commands
        """
        logger.info(f"Batch executing {len(device_commands)} device commands")
        
        # Run all commands concurrently (not waiting for timeouts)
        tasks = [
            self.execute_with_timeout(cmd, executor_func)
            for cmd in device_commands
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successes from failures
        successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
        timeouts = [r for r in results if isinstance(r, dict) and r.get("status") == "timeout"]
        errors = [r for r in results if isinstance(r, dict) and r.get("status") == "error"]
        
        return {
            "status": "batch_complete",
            "total": len(device_commands),
            "successful": len(successful),
            "timeouts": len(timeouts),
            "errors": len(errors),
            "results": results,
            "message": f"Batch: {len(successful)} success, {len(timeouts)} timeout, {len(errors)} error"
        }

    def get_command_history(self, limit: int = 20) -> list:
        """Return last N device commands for debugging."""
        sorted_history = sorted(
            self.command_history.items(),
            key=lambda x: x[1].get("timestamp", datetime.now()),
            reverse=True
        )[:limit]
        return [v for k, v in sorted_history]


# Singleton instance
device_executor = DeviceExecutorWithTimeout()
