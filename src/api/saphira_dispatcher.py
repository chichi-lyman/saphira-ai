# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

from src.core.novareign_a11y_parser import NovaReignScreenParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraDispatcher")


class ClientEvent(BaseModel):
    event_type: str = Field(..., description="E.g., 'user_voice_chunk', 'text_intent', 'a11y_screen_state'")
    session_id: str
    target_agent: Optional[str] = Field(default="saphira", description="Target agent key or 'auto'")
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


class AgentResponse(BaseModel):
    source_agent: str
    event_type: str
    payload: Dict[str, Any]
    requires_client_action: bool = False


class NovaAgentRegistry:
    SUPPORTED_AGENTS = {
        "saphira": "Personal AI Assistant & Intent Orchestrator",
        "aura": "Sensory, Audio & Speech Processing Agent",
        "agent_two": "Context, Memory Ledger & Knowledge Router",
        "novareign": "System Automation & Accessibility Executor",
        "novaaethrea": "High-Level Reasoning & Strategic Planner",
        "agent_zero": "Core Security, Policy Guardrails & Override",
    }

    @classmethod
    def resolve_target_agent(cls, event: ClientEvent) -> str:
        if event.target_agent and event.target_agent in cls.SUPPORTED_AGENTS:
            return event.target_agent

        event_type = event.event_type.lower()
        if "a11y" in event_type or "screen" in event_type or "click" in event_type:
            return "novareign"
        elif "audio" in event_type or "voice" in event_type:
            return "aura"
        elif "memory" in event_type or "recall" in event_type:
            return "agent_two"

        return "saphira"


class AgentExecutionEngine:
    @staticmethod
    async def dispatch_to_agent(agent_key: str, event: ClientEvent) -> AgentResponse:
        logger.info(f"[Nova Pipeline] Routing event '{event.event_type}' to agent: {agent_key}")

        if agent_key == "novareign":
            # Extract raw accessibility tree from payload and parse UI map
            raw_tree = event.payload.get("screen_tree", {})
            target_intent = event.payload.get("target_intent")

            if raw_tree:
                screen_state = NovaReignScreenParser.parse_raw_tree(raw_tree)
                
                # Resolve natural language target intent to specific element or tap center
                if target_intent:
                    action_plan = NovaReignScreenParser.resolve_target_action(screen_state, target_intent)
                else:
                    action_plan = {
                        "action": "screen_parsed",
                        "interactive_count": len(screen_state.interactive_elements),
                        "focused_input": screen_state.focused_input.node_id if screen_state.focused_input else None,
                    }

                return AgentResponse(
                    source_agent="novareign",
                    event_type="execute_a11y_command",
                    payload={"package_name": screen_state.package_name, "action_plan": action_plan},
                    requires_client_action=True,
                )

            # Fallback for explicit raw action pass-through
            action_payload = event.payload.get("action", {})
            return AgentResponse(
                source_agent="novareign",
                event_type="execute_a11y_command",
                payload={"command": action_payload.get("command"), "target": action_payload.get("target")},
                requires_client_action=True,
            )

        elif agent_key == "aura":
            return AgentResponse(
                source_agent="aura",
                event_type="audio_processed",
                payload={"status": "received", "sample_rate": 16000},
            )
        else:
            return AgentResponse(
                source_agent="saphira",
                event_type="text_response",
                payload={"text": f"Saphira received intent via {agent_key}: {event.payload.get('content', '')}"},
            )


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"[Dispatcher] Client connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"[Dispatcher] Client disconnected: {session_id}")

    async def send_response(self, session_id: str, response: AgentResponse):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(response.model_dump_json())


manager = ConnectionManager()
router = APIRouter(prefix="/v1/saphira", tags=["Saphira WebSocket Dispatcher"])


@router.websocket("/stream")
async def websocket_dispatcher_endpoint(websocket: WebSocket):
    session_id = websocket.query_params.get("session_id", "default_android_client")
    await manager.connect(session_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data_dict = json.loads(raw_data)

            client_event = ClientEvent(**data_dict)
            target_agent = NovaAgentRegistry.resolve_target_agent(client_event)
            agent_response = await AgentExecutionEngine.dispatch_to_agent(target_agent, client_event)

            await manager.send_response(session_id, agent_response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"[Dispatcher Error] Session {session_id}: {str(e)}")
        manager.disconnect(session_id)
