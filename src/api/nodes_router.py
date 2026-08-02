# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
FastAPI router for Saphira Nodes — registration, pairing, invoke.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.nodes.registry import node_registry
from src.nodes.invoke import node_invoker

router = APIRouter(prefix="/nodes", tags=["nodes"])


class RegisterNodeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    node_type: str = Field(
        "headless",
        description="headless | vscode | canvas | media | mobile_ios | mobile_android | custom",
    )
    host: Optional[str] = None
    platform: Optional[str] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_approve: bool = False


class InvokeRequest(BaseModel):
    node: str = Field(..., description="Node id or name")
    command: str = Field(..., description="e.g. camera.snap, code.write, canvas.dashboard")
    params: Optional[Dict[str, Any]] = None


class InvokeAnyRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None
    preferred_type: Optional[str] = None


@router.get("")
async def list_nodes(status: Optional[str] = None, node_type: Optional[str] = None):
    return {"nodes": node_registry.list(status=status, node_type=node_type)}


@router.get("/status")
async def nodes_status():
    return node_registry.status_summary()


@router.post("/register")
async def register_node(req: RegisterNodeRequest):
    try:
        node = node_registry.register(
            name=req.name,
            node_type=req.node_type,
            host=req.host,
            platform=req.platform,
            capabilities=req.capabilities,
            metadata=req.metadata,
            auto_approve=req.auto_approve,
        )
        return {"status": "registered", "node": node.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{id_or_name}/approve")
async def approve_node(id_or_name: str):
    node = node_registry.approve(id_or_name)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "approved", "node": node.to_dict()}


@router.post("/{id_or_name}/reject")
async def reject_node(id_or_name: str):
    node = node_registry.reject(id_or_name)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "rejected", "node": node.to_dict()}


@router.delete("/{id_or_name}")
async def remove_node(id_or_name: str):
    if not node_registry.remove(id_or_name):
        raise HTTPException(status_code=404, detail="Node not found")
    return {"status": "removed", "id_or_name": id_or_name}


@router.get("/{id_or_name}")
async def get_node(id_or_name: str):
    node = node_registry.get(id_or_name)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node.to_dict()


@router.post("/invoke")
async def invoke_node(req: InvokeRequest):
    result = await node_invoker.invoke(req.node, req.command, req.params)
    if result.get("error") == "NODE_NOT_FOUND":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/invoke-any")
async def invoke_any(req: InvokeAnyRequest):
    return await node_invoker.invoke_any(
        req.command, req.params, preferred_type=req.preferred_type
    )
