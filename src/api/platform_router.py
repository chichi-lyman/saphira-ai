"""Platform API: autonomy, memory, voice, entitlements, evidence, devices."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.platform.policy import AutonomyPolicy, CounterfactualPreview
from src.platform.memory import memory_store
from src.platform.voice import voice_sessions, AvatarState
from src.platform.entitlements import entitlements
from src.platform.evidence import evidence_exporter, issue_receipt
from src.platform.devices import matter_bridge, DeviceCommand, offline_queue
from src.platform.identity import identity_service, Principal
from src.platform.plugins import plugin_registry, PluginSpec
from src.platform.observability_ext import model_router

router = APIRouter(prefix="/platform", tags=["platform"])


class AutonomyRequest(BaseModel):
    capability: str
    tenant_id: str = "default"
    confirmed: bool = False
    intent: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)


class MemoryAddRequest(BaseModel):
    tenant_id: str
    user_id: str
    content: str
    kind: str = "episodic"
    confidence: float = 1.0


class VoiceSessionRequest(BaseModel):
    tenant_id: str
    user_id: str


class VoiceStateRequest(BaseModel):
    state: str


class EntitlementAssignRequest(BaseModel):
    tenant_id: str
    plan: str = "free"


class DevicePlanRequest(BaseModel):
    device_id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False


class OfflineIntentRequest(BaseModel):
    tenant_id: str
    user_id: str
    text: str


@router.get("/health")
async def platform_health() -> Dict[str, Any]:
    return {"status": "healthy", "layer": "platform", "version": "1.0.0"}


@router.post("/autonomy/decide")
async def autonomy_decide(req: AutonomyRequest) -> Dict[str, Any]:
    policy = AutonomyPolicy(tenant_id=req.tenant_id)
    decision = policy.decide(req.capability, {"confirmed": req.confirmed, "side_effects": req.side_effects})
    preview = None
    if decision.requires_confirmation:
        preview = CounterfactualPreview.build(intent=req.intent or req.capability, capability=req.capability, tools=req.tools, side_effects=req.side_effects)
    return {"allowed": decision.allowed, "level": decision.level.value, "requires_confirmation": decision.requires_confirmation, "reason": decision.reason, "preview": preview}


@router.post("/memory")
async def memory_add(req: MemoryAddRequest) -> Dict[str, Any]:
    rec = memory_store.add(req.tenant_id, req.user_id, req.content, req.kind, req.confidence)
    return {"id": rec.id, "kind": rec.kind, "namespace": memory_store.isolation_key(req.tenant_id, req.user_id)}


@router.get("/memory/{tenant_id}/{user_id}")
async def memory_list(tenant_id: str, user_id: str, kind: Optional[str] = None) -> Dict[str, Any]:
    rows = memory_store.list_for_user(tenant_id, user_id, kind)
    return {"count": len(rows), "items": [{"id": r.id, "kind": r.kind, "content": r.content, "confidence": r.confidence} for r in rows]}


@router.post("/voice/sessions")
async def voice_create(req: VoiceSessionRequest) -> Dict[str, Any]:
    sess = voice_sessions.create(req.tenant_id, req.user_id)
    return {"session_id": sess.session_id, "avatar_state": sess.avatar_state.value}


@router.post("/voice/sessions/{session_id}/state")
async def voice_state(session_id: str, req: VoiceStateRequest) -> Dict[str, Any]:
    try:
        state = AvatarState(req.state)
    except ValueError:
        return {"status": "error", "message": f"Invalid state: {req.state}"}
    sess = voice_sessions.set_state(session_id, state)
    if not sess:
        return {"status": "error", "message": "Session not found"}
    return {"session_id": session_id, "avatar_state": sess.avatar_state.value}


@router.post("/entitlements/assign")
async def entitlements_assign(req: EntitlementAssignRequest) -> Dict[str, Any]:
    ent = entitlements.assign(req.tenant_id, req.plan)
    return {"tenant_id": ent.tenant_id, "plan": ent.plan.name, "limits": {"api_calls_monthly": ent.plan.api_calls_monthly, "agent_minutes_monthly": ent.plan.agent_minutes_monthly, "seats": ent.plan.seats, "autonomy_max": ent.plan.autonomy_max}}


@router.post("/devices/plan")
async def devices_plan(req: DevicePlanRequest) -> Dict[str, Any]:
    return matter_bridge.plan(DeviceCommand(device_id=req.device_id, action=req.action, params=req.params), confirmed=req.confirmed)


@router.post("/offline/enqueue")
async def offline_enqueue(req: OfflineIntentRequest) -> Dict[str, Any]:
    item = offline_queue.enqueue(req.tenant_id, req.user_id, req.text)
    return {"id": item.id, "pending": offline_queue.pending_count()}


@router.get("/models/{task_class}")
async def model_for_task(task_class: str) -> Dict[str, Any]:
    route = model_router.resolve(task_class)
    return {"task_class": route.task_class, "provider": route.provider, "model": route.model, "max_latency_ms": route.max_latency_ms, "cost_tier": route.cost_tier}


@router.post("/identity/api-keys")
async def issue_key(tenant_id: str = "default") -> Dict[str, Any]:
    token = identity_service.issue_api_key(tenant_id)
    return {"api_key": token, "note": "Store once; only hash is retained server-side."}


@router.get("/identity/permissions")
async def permissions(subject_id: str, tenant_id: str = "default", role: str = "operator") -> Dict[str, Any]:
    principal = Principal(subject_id=subject_id, tenant_id=tenant_id, roles=[role])
    return {"subject_id": subject_id, "roles": principal.roles, "permissions": sorted(principal.permissions()), "agent_did": identity_service.agent_did(tenant_id, subject_id)}


@router.post("/evidence/export")
async def export_evidence(tenant_id: str = "default") -> Dict[str, Any]:
    pack = evidence_exporter.export(tenant_id, records=[], model_versions=["saphira-17.0.0"])
    return {"tenant_id": pack.tenant_id, "generated_at": pack.generated_at, "json": pack.to_json()}


@router.post("/receipts")
async def create_receipt(tenant_id: str, actor: str, capability: str, policy_decision: str = "ALLOW", model_version: str = "saphira-17.0.0") -> Dict[str, Any]:
    receipt = issue_receipt(tenant_id=tenant_id, actor=actor, capability=capability, policy_decision=policy_decision, model_version=model_version, input_payload={"capability": capability})
    return {"receipt_id": receipt.receipt_id, "input_hash": receipt.input_hash, "chain_hash": receipt.chain_hash()}


@router.post("/plugins/register")
async def register_plugin(name: str, version: str = "1.0.0", risk_tier: str = "low") -> Dict[str, Any]:
    plugin_registry.register(PluginSpec(name=name, version=version, risk_tier=risk_tier))
    return {"registered": name, "risk_tier": risk_tier}


@router.get("/plugins")
async def list_plugins() -> Dict[str, Any]:
    items = {name: {"version": p.version, "risk_tier": p.risk_tier} for name, p in plugin_registry.list().items()}
    return {"plugins": items}
