# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Saphira WebSocket dispatcher with excellence-aware routing.

User-facing voice remains Saphira only. Internal agents receive capability-aware
routes from ExcellenceRouter before execution. LoopGuard blocks identical cycles.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from src.core.novareign_a11y_parser import NovaReignScreenParser
from src.excellence.router import ExcellenceRouter, route_excellence
from src.excellence.agent_map import pillars_for_agent
from src.excellence.telemetry import excellence_telemetry
from src.latency.router import LatencyRouter
from src.privacy.filter import PrivacyFilter
from src.memory.ledger import dual_memory
from src.autonomy.loop_guard import global_loop_guard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraDispatcher")

_excellence = ExcellenceRouter()
_latency = LatencyRouter()
_privacy = PrivacyFilter()


class ClientEvent(BaseModel):
    event_type: str = Field(
        ..., description="E.g., 'user_voice_chunk', 'text_intent', 'a11y_screen_state'"
    )
    session_id: str
    target_agent: Optional[str] = Field(
        default="saphira", description="Target agent key or 'auto'"
    )
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


class AgentResponse(BaseModel):
    source_agent: str
    event_type: str
    payload: Dict[str, Any]
    requires_client_action: bool = False
    excellence: Optional[Dict[str, Any]] = None


class NovaAgentRegistry:
    """Internal agent roster. Only 'saphira' is spoken to the user."""

    SUPPORTED_AGENTS = {
        "saphira": "Personal AI Assistant & Intent Orchestrator",
        "aura": "Voice & Real-Time Interaction (latency / edge audio)",
        "agent_zero": "Edge Orchestration & Local Execution",
        "agent_two": "Tools & Web Operations (tool_automation)",
        "novareign": "UI & Accessibility Layer",
        "novaaethrea": "Context & Long-Term Memory (memory_hybrid)",
        "scholar": "Deep Reasoning & Analysis",
        "cipher": "Security & Audit Ledger (privacy_ledger)",
    }

    PILLAR_AGENT = {
        "latency": "aura",
        "edge": "agent_zero",
        "automation": "agent_two",
        "memory": "novaaethrea",
        "reasoning": "scholar",
        "privacy": "cipher",
    }

    @classmethod
    def resolve_target_agent(
        cls,
        event: ClientEvent,
        excellence_routes: Optional[List[Any]] = None,
    ) -> str:
        if event.target_agent and event.target_agent in cls.SUPPORTED_AGENTS:
            if event.target_agent != "auto":
                return event.target_agent

        event_type = event.event_type.lower()
        if "a11y" in event_type or "screen" in event_type or "click" in event_type:
            return "novareign"
        if "audio" in event_type or "voice" in event_type:
            return "aura"
        if "memory" in event_type or "recall" in event_type:
            return "novaaethrea"
        if "reason" in event_type or "analyze" in event_type:
            return "scholar"
        if "security" in event_type or "audit" in event_type:
            return "cipher"
        if "offline" in event_type or "edge" in event_type:
            return "agent_zero"
        if "tool" in event_type or "web" in event_type:
            return "agent_two"

        if excellence_routes:
            for route in excellence_routes:
                pillar = getattr(route, "pillar_id", None) or (
                    route.get("pillar_id") if isinstance(route, dict) else None
                )
                if pillar in cls.PILLAR_AGENT and pillar not in (
                    "latency",
                    "privacy",
                    "overall",
                ):
                    return cls.PILLAR_AGENT[pillar]

        return "saphira"


class AgentExecutionEngine:
    @staticmethod
    async def dispatch_to_agent(
        agent_key: str,
        event: ClientEvent,
        *,
        excellence_meta: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        logger.info(
            "[Nova Pipeline] Routing event '%s' to agent: %s pillars=%s",
            event.event_type,
            agent_key,
            pillars_for_agent(agent_key),
        )

        if agent_key == "novareign":
            raw_tree = event.payload.get("screen_tree", {})
            target_intent = event.payload.get("target_intent")

            if raw_tree:
                screen_state = NovaReignScreenParser.parse_raw_tree(raw_tree)
                if target_intent:
                    action_plan = NovaReignScreenParser.resolve_target_action(
                        screen_state, target_intent
                    )
                else:
                    action_plan = {
                        "action": "screen_parsed",
                        "interactive_count": len(screen_state.interactive_elements),
                        "focused_input": (
                            screen_state.focused_input.node_id
                            if screen_state.focused_input
                            else None
                        ),
                    }

                return AgentResponse(
                    source_agent="novareign",
                    event_type="execute_a11y_command",
                    payload={
                        "package_name": screen_state.package_name,
                        "action_plan": action_plan,
                    },
                    requires_client_action=True,
                    excellence=excellence_meta,
                )

            action_payload = event.payload.get("action", {})
            return AgentResponse(
                source_agent="novareign",
                event_type="execute_a11y_command",
                payload={
                    "command": action_payload.get("command"),
                    "target": action_payload.get("target"),
                },
                requires_client_action=True,
                excellence=excellence_meta,
            )

        if agent_key == "aura":
            return AgentResponse(
                source_agent="aura",
                event_type="audio_processed",
                payload={
                    "status": "received",
                    "sample_rate": 16000,
                    "latency_path": (excellence_meta or {}).get("latency_path"),
                },
                excellence=excellence_meta,
            )

        if agent_key == "novaaethrea":
            mem = dual_memory.memory_check()
            return AgentResponse(
                source_agent="novaaethrea",
                event_type="memory_context",
                payload={"memory_check": mem, "context_pack": dual_memory.context_pack()},
                excellence=excellence_meta,
            )

        if agent_key == "scholar":
            content = event.payload.get("content", "")
            return AgentResponse(
                source_agent="scholar",
                event_type="reasoning_plan",
                payload={"status": "queued", "task": content, "mode": "multi_step"},
                excellence=excellence_meta,
            )

        if agent_key == "cipher":
            return AgentResponse(
                source_agent="cipher",
                event_type="audit_ack",
                payload={"status": "ledger_ready", "zero_egress": True},
                excellence=excellence_meta,
            )

        if agent_key == "agent_zero":
            return AgentResponse(
                source_agent="agent_zero",
                event_type="edge_ready",
                payload={"status": "local_execution_armed", "offline_capable": True},
                excellence=excellence_meta,
            )

        if agent_key == "agent_two":
            return AgentResponse(
                source_agent="agent_two",
                event_type="tool_plan",
                payload={
                    "status": "tools_ready",
                    "policy_gated": True,
                    "task": event.payload.get("content", ""),
                },
                excellence=excellence_meta,
            )

        content = event.payload.get("content", "")
        return AgentResponse(
            source_agent="saphira",
            event_type="text_response",
            payload={
                "text": (
                    f"Saphira received your request"
                    + (f": {content}" if content else ".")
                )
            },
            excellence=excellence_meta,
        )


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("[Dispatcher] Client connected: %s", session_id)

    def disconnect(self, session_id: str) -> None:
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            global_loop_guard.reset_session(session_id)
            logger.info("[Dispatcher] Client disconnected: %s", session_id)

    async def send_response(self, session_id: str, response: AgentResponse) -> None:
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(response.model_dump_json())


manager = ConnectionManager()
router = APIRouter(prefix="/v1/saphira", tags=["Saphira WebSocket Dispatcher"])


def _utterance_from_event(event: ClientEvent) -> str:
    payload = event.payload or {}
    for key in ("content", "text", "transcript", "target_intent"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return event.event_type


@router.websocket("/stream")
async def websocket_dispatcher_endpoint(websocket: WebSocket):
    session_id = websocket.query_params.get("session_id", "default_android_client")
    await manager.connect(session_id, websocket)

    try:
        while True:
            t0 = time.perf_counter()
            raw_data = await websocket.receive_text()
            data_dict = json.loads(raw_data)
            client_event = ClientEvent(**data_dict)

            utterance = _utterance_from_event(client_event)
            sanitized = _privacy.sanitize_text(utterance)
            if sanitized.redacted and "content" in client_event.payload:
                client_event.payload["content"] = sanitized.text

            excellence_routes = route_excellence(sanitized.text)
            latency = _latency.decide(
                task=sanitized.text,
                prefer_gpu="gpu" in sanitized.text.lower()
                or client_event.event_type.lower().startswith("voice"),
                offline=bool(client_event.payload.get("force_offline")),
            )

            dual_memory.append_turn(
                "user",
                sanitized.text,
                session_id=client_event.session_id,
                event_type=client_event.event_type,
            )

            target_agent = NovaAgentRegistry.resolve_target_agent(
                client_event, excellence_routes
            )

            # LoopGuard before dispatch — identical cycles are blocked
            loop_verdict = global_loop_guard.check(
                session_id=client_event.session_id or session_id,
                agent=target_agent,
                intent=sanitized.text or client_event.event_type,
                record=True,
            )
            if not loop_verdict.allowed:
                blocked = AgentResponse(
                    source_agent="saphira",
                    event_type="text_response",
                    payload={
                        "text": (
                            "I'm already working on that. "
                            "Want me to try a different approach?"
                        ),
                        "loop_blocked": True,
                        "retry_after_sec": loop_verdict.suggested_retry_after_sec,
                    },
                    excellence={
                        "loop": {
                            "allowed": False,
                            "reason": loop_verdict.reason,
                            "fingerprint": loop_verdict.fingerprint,
                            "retry_after_sec": loop_verdict.suggested_retry_after_sec,
                        },
                        "surface_agent": "Saphira",
                        "internal_agent": target_agent,
                    },
                )
                excellence_telemetry.record_dispatch(
                    agent=target_agent,
                    latency_path="loop_blocked",
                    elapsed_ms=int((time.perf_counter() - t0) * 1000),
                    pillars=["loop_prevention"],
                )
                await manager.send_response(session_id, blocked)
                continue

            excellence_meta = {
                "routes": [
                    {
                        "pillar": r.pillar_id,
                        "capability": r.capability,
                        "plugin": r.plugin,
                        "owners": list(r.internal_owners),
                    }
                    for r in excellence_routes
                ],
                "latency_path": latency.path,
                "estimated_ttft_ms": latency.estimated_ttft_ms,
                "privacy_redacted": sanitized.redacted,
                "internal_agent": target_agent,
                "surface_agent": "Saphira",
                "loop": {
                    "allowed": True,
                    "fingerprint": loop_verdict.fingerprint,
                    "prior_count": loop_verdict.prior_count,
                },
            }

            agent_response = await AgentExecutionEngine.dispatch_to_agent(
                target_agent, client_event, excellence_meta=excellence_meta
            )

            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            excellence_telemetry.record_dispatch(
                agent=target_agent,
                latency_path=latency.path,
                elapsed_ms=elapsed_ms,
                pillars=[r.pillar_id for r in excellence_routes],
            )

            await manager.send_response(session_id, agent_response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error("[Dispatcher Error] Session %s: %s", session_id, e)
        manager.disconnect(session_id)


@router.get("/excellence/stats")
async def excellence_stats() -> Dict[str, Any]:
    """Live excellence telemetry for latency and routing."""
    return excellence_telemetry.snapshot()
