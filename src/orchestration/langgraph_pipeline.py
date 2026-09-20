# Copyright © 2026 Chelsea Megan Woods
"""
LangGraph-based pipeline adapter for the immutable Saphira chain:
Saphira → Aura → Agent Two → NovaReign → NovaAethrea → Agent Zero

Specialists (Apex, Lexis, Instinct, Cipher, Scholar, Lyra) are fan-out only
from NovaReign and never bypass security or governance.
"""

from __future__ import annotations

from typing import Any, TypedDict, Annotated
import operator

try:
    from langgraph.graph import StateGraph, END
except ImportError:  # pragma: no cover — optional until deps installed
    StateGraph = None  # type: ignore
    END = None  # type: ignore


class PipelineState(TypedDict, total=False):
    user_input: str
    context: dict[str, Any]
    intent: str
    perception: dict[str, Any]
    security_status: str
    policy: str
    memory_pack: dict[str, Any]
    execution_result: dict[str, Any]
    specialist_outputs: Annotated[list[dict[str, Any]], operator.add]
    messages: Annotated[list[str], operator.add]
    status: str


def _node_saphira(state: PipelineState) -> dict[str, Any]:
    return {
        "intent": state.get("intent") or "general",
        "messages": ["saphira:intent_parsed"],
        "status": "running",
    }


def _node_aura(state: PipelineState) -> dict[str, Any]:
    return {
        "perception": state.get("perception") or {"ok": True},
        "messages": ["aura:perception_ready"],
    }


def _node_agent_two(state: PipelineState) -> dict[str, Any]:
    # Default GREEN; real implementation consults Agent Two
    return {
        "security_status": state.get("security_status") or "GREEN",
        "messages": ["agent_two:security_scanned"],
    }


def _node_nova_reign(state: PipelineState) -> dict[str, Any]:
    if state.get("security_status") == "RED":
        return {"policy": "DENY", "status": "blocked", "messages": ["nova_reign:denied"]}
    return {
        "policy": state.get("policy") or "ALLOW",
        "messages": ["nova_reign:governed"],
    }


def _node_nova_aethrea(state: PipelineState) -> dict[str, Any]:
    return {
        "memory_pack": state.get("memory_pack") or {"facts": {}},
        "messages": ["nova_aethrea:context_loaded"],
    }


def _node_agent_zero(state: PipelineState) -> dict[str, Any]:
    if state.get("policy") == "DENY":
        return {"execution_result": {"status": "skipped"}, "status": "blocked"}
    return {
        "execution_result": {"status": "ok"},
        "status": "success",
        "messages": ["agent_zero:executed"],
    }


def build_saphira_graph():
    """Compile the fixed sequential pipeline as a LangGraph StateGraph."""
    if StateGraph is None:
        raise ImportError("langgraph is required: pip install langgraph")

    graph = StateGraph(PipelineState)
    graph.add_node("saphira", _node_saphira)
    graph.add_node("aura", _node_aura)
    graph.add_node("agent_two", _node_agent_two)
    graph.add_node("nova_reign", _node_nova_reign)
    graph.add_node("nova_aethrea", _node_nova_aethrea)
    graph.add_node("agent_zero", _node_agent_zero)

    graph.set_entry_point("saphira")
    graph.add_edge("saphira", "aura")
    graph.add_edge("aura", "agent_two")
    graph.add_edge("agent_two", "nova_reign")
    graph.add_edge("nova_reign", "nova_aethrea")
    graph.add_edge("nova_aethrea", "agent_zero")
    graph.add_edge("agent_zero", END)

    return graph.compile()
