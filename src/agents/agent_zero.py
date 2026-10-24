# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Agent Zero — Terminal Execution Engine
# Position: Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero
# Responsible for side-effecting actions only after policy clearance.

from __future__ import annotations

from typing import Any, Dict, Optional
import logging
import time

from src.connectors.matter_home_assistant import matter_ha

logger = logging.getLogger("AgentZero")


class AgentZero:
    """Hands-on execution engine.

    Receives fully authorized payloads from upstream agents and performs
    the actual work (smart-home, registered tools, system actions).
    Never plans or decides policy — only executes.
    """

    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha
        self._tool_handlers: Dict[str, Any] = {}

    def register_tool(self, name: str, handler) -> None:
        """Allow capability-registry / mcp-builder outputs to be registered at runtime."""
        self._tool_handlers[name] = handler
        logger.info("Registered execution tool: %s", name)

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        started = time.monotonic()
        action = payload.get("action") or payload.get("tool") or ""
        params = payload.get("params") or payload.get("arguments") or {}
        request_id = payload.get("request_id") or payload.get("trace_id")

        try:
            # 1. Smart-home / Matter path
            if action in {
                "turn_on", "turn_off", "toggle", "set_brightness",
                "set_temperature", "lock", "unlock", "set_cover", "matter",
            }:
                result = self.matter.execute_intent(action, params)
                return self._result(
                    status=result.get("status", "unknown"),
                    action=action,
                    result=result,
                    request_id=request_id,
                    latency_ms=self._ms(started),
                )

            # 2. Explicitly registered tools (from capability registry / MCP)
            if action in self._tool_handlers:
                handler = self._tool_handlers[action]
                if callable(handler):
                    out = handler(params) if not hasattr(handler, "__await__") else await handler(params)
                    return self._result(
                        status="success",
                        action=action,
                        result=out,
                        request_id=request_id,
                        latency_ms=self._ms(started),
                    )

            # 3. Generic structured execution request (future expansion point)
            #    Keep this path strict — only accept well-formed, pre-authorized payloads.
            if action:
                logger.info(
                    "Execution accepted (generic): action=%s request_id=%s",
                    action, request_id,
                )
                return self._result(
                    status="accepted",
                    action=action,
                    result={
                        "message": f"Execution request accepted for action '{action}'",
                        "params": params,
                    },
                    request_id=request_id,
                    latency_ms=self._ms(started),
                )

            return self._result(
                status="error",
                action=action or "none",
                result={"error": "No action or tool specified"},
                request_id=request_id,
                latency_ms=self._ms(started),
            )

        except Exception as exc:
            logger.exception("Agent Zero execution failure: %s", exc)
            return self._result(
                status="error",
                action=action or "unknown",
                result={"error": str(exc)},
                request_id=request_id,
                latency_ms=self._ms(started),
            )

    @staticmethod
    def _ms(started: float) -> int:
        return int((time.monotonic() - started) * 1000)

    @staticmethod
    def _result(
        *,
        status: str,
        action: str,
        result: Any,
        request_id: Optional[str],
        latency_ms: int,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "agent": "agent_zero",
            "action": action,
            "result": result,
            "request_id": request_id,
            "latency_ms": latency_ms,
        }
