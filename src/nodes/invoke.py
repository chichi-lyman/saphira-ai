# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Node invoke layer — routes commands to the appropriate handler.

In production these handlers would talk over WebSocket / device pairing
to real companion apps. Here we provide structured stubs + local
simulation so the orchestrator and Agent Zero can already call the surface.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import logging
import time

from .base import Node, NodeStatus, NodeCapability
from .registry import node_registry
from .handlers import (
    code_handler,
    media_handler,
    canvas_handler,
    camera_handler,
    system_handler,
)

logger = logging.getLogger("SaphiraNodeInvoke")

HANDLER_MAP = {
    "code": code_handler.handle,
    "media": media_handler.handle,
    "canvas": canvas_handler.handle,
    "camera": camera_handler.handle,
    "device": system_handler.handle_device,
    "notifications": system_handler.handle_notifications,
    "system": system_handler.handle_system,
}


class NodeInvoker:
    """High-level API used by the gateway / Agent Zero."""

    def __init__(self, registry=None):
        self.registry = registry or node_registry

    async def invoke(
        self,
        node_id_or_name: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a command on a specific node.

        command examples:
          - code.write
          - camera.snap
          - canvas.dashboard
          - media.viz
          - system.exec
        """
        params = params or {}
        node = self.registry.get(node_id_or_name)

        if not node:
            return {
                "status": "error",
                "error": "NODE_NOT_FOUND",
                "message": f"No node matching '{node_id_or_name}'.",
            }

        if node.status != NodeStatus.ONLINE:
            return {
                "status": "error",
                "error": "NODE_NOT_ONLINE",
                "message": f"Node '{node.name}' is {node.status.value}.",
                "node_id": node.id,
            }

        if not node.has_capability(command):
            return {
                "status": "error",
                "error": "CAPABILITY_DENIED",
                "message": f"Node '{node.name}' does not expose '{command}'.",
                "available": [c.value for c in node.capabilities],
            }

        # Allowlist check (optional tighter gate)
        if node.allowlist:
            family = command.split(".")[0]
            if not any(command.startswith(a) or family == a for a in node.allowlist):
                return {
                    "status": "error",
                    "error": "ALLOWLIST_DENIED",
                    "message": f"Command '{command}' not in node allowlist.",
                }

        family = command.split(".")[0]
        handler = HANDLER_MAP.get(family)
        if not handler:
            return {
                "status": "error",
                "error": "UNKNOWN_FAMILY",
                "message": f"No handler for command family '{family}'.",
            }

        node.touch()
        started = time.time()
        try:
            result = await handler(node, command, params)
            result.setdefault("node_id", node.id)
            result.setdefault("node_name", node.name)
            result.setdefault("command", command)
            result.setdefault("duration_ms", int((time.time() - started) * 1000))
            return result
        except Exception as e:
            logger.exception("Invoke failed on %s for %s", node.id, command)
            return {
                "status": "error",
                "error": "INVOKE_EXCEPTION",
                "message": str(e),
                "node_id": node.id,
                "command": command,
            }

    async def invoke_any(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        preferred_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pick the best online node that supports the command and invoke it."""
        candidates = self.registry.find_by_capability(command)
        if preferred_type:
            typed = [n for n in candidates if n.node_type.value == preferred_type]
            if typed:
                candidates = typed
        if not candidates:
            return {
                "status": "error",
                "error": "NO_CAPABLE_NODE",
                "message": f"No online node supports '{command}'.",
            }
        # Prefer most recently seen
        candidates.sort(key=lambda n: n.last_seen or 0, reverse=True)
        return await self.invoke(candidates[0].id, command, params)


node_invoker = NodeInvoker()
