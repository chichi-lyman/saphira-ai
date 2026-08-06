# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Secure tool / function-calling registry with autonomy guardrails.

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

from src.core.autonomy_levels import SaphiraAutonomy

logger = logging.getLogger("SaphiraTools")

ToolHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass
class ToolSpec:
    name: str
    description: str
    autonomy: str  # L1 / L2 / L3
    handler: Optional[ToolHandler] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"
    enabled: bool = True

    def openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {"type": "object", "properties": {}},
            },
        }


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._register_defaults()

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for t in self._tools.values():
            if not t.enabled:
                continue
            if category and t.category != category:
                continue
            out.append({
                "name": t.name,
                "description": t.description,
                "autonomy": t.autonomy,
                "category": t.category,
            })
        return out

    def schemas_for_llm(self) -> List[Dict[str, Any]]:
        return [t.openai_schema() for t in self._tools.values() if t.enabled and t.handler]

    async def execute(
        self,
        name: str,
        args: Optional[Dict[str, Any]] = None,
        *,
        confirmed: bool = False,
    ) -> Dict[str, Any]:
        args = args or {}
        tool = self._tools.get(name)
        if not tool or not tool.enabled:
            return {"status": "error", "message": f"Unknown or disabled tool: {name}"}

        if tool.autonomy == SaphiraAutonomy.L1_CONFIRM_FIRST.value and not confirmed:
            return {
                "status": "needs_confirmation",
                "tool": name,
                "message": f"I need your OK before I run '{name}'.",
                "args": args,
            }

        if tool.handler is None:
            return {
                "status": "success",
                "tool": name,
                "summary": f"Tool '{name}' acknowledged (handler not wired yet).",
                "stub": True,
            }

        try:
            result = await tool.handler(args)
            return {"status": "success", "tool": name, **(result or {})}
        except Exception as e:
            logger.exception("Tool %s failed", name)
            return {
                "status": "error",
                "tool": name,
                "message": "That didn't work cleanly — I stopped before anything unsafe.",
                "error": str(e),
            }

    def _register_defaults(self) -> None:
        defaults = [
            ToolSpec(
                name="web_search",
                description="Search the live web for current information",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="info",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
            ToolSpec(
                name="calendar_list",
                description="List upcoming calendar events",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="productivity",
            ),
            ToolSpec(
                name="calendar_create",
                description="Create a calendar event",
                autonomy=SaphiraAutonomy.L1_CONFIRM_FIRST.value,
                category="productivity",
            ),
            ToolSpec(
                name="send_notification",
                description="Send a local or push notification to the user",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="system",
            ),
            ToolSpec(
                name="iot_lights",
                description="Control smart lights (power/color)",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="iot",
            ),
            ToolSpec(
                name="iot_vacuum",
                description="Control robotic vacuum",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="iot",
            ),
            ToolSpec(
                name="iot_media",
                description="Control media playback / channels",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="iot",
            ),
            ToolSpec(
                name="iot_bed",
                description="Adjust smart bed position",
                autonomy=SaphiraAutonomy.L2_SUPERVISED.value,
                category="iot",
            ),
            ToolSpec(
                name="shell_command",
                description="Run a local shell command (restricted)",
                autonomy=SaphiraAutonomy.L1_CONFIRM_FIRST.value,
                category="system",
                parameters={
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
            ),
            ToolSpec(
                name="memory_write",
                description="Store a long-term preference or fact",
                autonomy=SaphiraAutonomy.L3_BACKGROUND.value,
                category="memory",
            ),
            ToolSpec(
                name="memory_search",
                description="Search long-term memory",
                autonomy=SaphiraAutonomy.L3_BACKGROUND.value,
                category="memory",
            ),
        ]
        for spec in defaults:
            self.register(spec)


tool_registry = ToolRegistry()
