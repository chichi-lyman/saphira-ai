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
from src.platform.biometrics import biometric_stress

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


class DeviceCommandRequest(BaseModel):
    device_id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False


class OfflineEnqueueRequest(BaseModel):
    tenant_id: str
    user_id: str
    intent: str


class PluginRegisterRequest(BaseModel):
    name: str
    version: str = "1.0"
    risk_tier: str = "low"


class PluginInvokeRequest(BaseModel):
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False


class ReceiptRequest(BaseModel):
    tenant_id: str
    actor: str
    capability: str
    decision: str
    message_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
async def platform_health():
    return {"status": "ok", "layer": "platform"}


@router.post("/autonomy/decide")
async def autonomy_decide(body: AutonomyRequest):
    policy = AutonomyPolicy(tenant_id=body.tenant_id)
    ctx = {
        "confirmed": body.confirmed,
        "intent": body.intent,
        "tools": body.tools,
        "side_effects": body.side_effects,
    }
    decision = policy.decide(body.capability, ctx)
    preview = None
    if decision.requires_confirmation:
        preview = CounterfactualPreview.build(
            intent=body.intent or body.capability,
            capability=body.capability,
            tools=body.tools,
            side_effects=body.side_effects,
        )
    return {
        "allowed": decision.allowed,
        "level": decision.level.value,
        "requires_confirmation": decision.requires_confirmation,
        "reason": decision.reason,
        "preview": preview,
    }


@router.post("/memory/add")
async def memory_add(body: MemoryAddRequest):
    rec = memory_store.add(body.tenant_id, body.user_id, body.content, body.kind, body.confidence)
    return {"id": rec.id, "kind": rec.kind}


@router.get("/memory/{tenant_id}/{user_id}")
async def memory_list(tenant_id: str, user_id: str):
    rows = memory_store.list_for_user(tenant_id, user_id)
    return {"count": len(rows), "items": [{"id": r.id, "content": r.content, "kind": r.kind} for r in rows]}


@router.post("/voice/session")
async def voice_create(body: VoiceSessionRequest):
    sess = voice_sessions.create(body.tenant_id, body.user_id)
    return {"session_id": sess.session_id, "state": sess.avatar_state.value}


@router.post("/voice/session/{session_id}/state")
async def voice_state(session_id: str, body: VoiceStateRequest):
    try:
        st = AvatarState(body.state)
    except ValueError:
        return {"error": "invalid state"}
    sess = voice_sessions.set_state(session_id, st)
    if not sess:
        return {"error": "session not found"}
    return {"session_id": session_id, "state": sess.avatar_state.value}


@router.post("/entitlements/assign")
async def entitlements_assign(body: EntitlementAssignRequest):
    ent = entitlements.assign(body.tenant_id, body.plan)
    return {"tenant_id": ent.tenant_id, "plan": ent.plan.name, "autonomy_max": ent.plan.autonomy_max}


@router.post("/devices/command")
async def device_command(body: DeviceCommandRequest):
    cmd = DeviceCommand(body.device_id, body.action, body.params)
    return matter_bridge.plan(cmd, confirmed=body.confirmed)


@router.post("/devices/offline")
async def offline_enqueue(body: OfflineEnqueueRequest):
    cmd = offline_queue.enqueue(body.tenant_id, body.user_id, body.intent)
    return {"id": cmd.id, "pending": offline_queue.pending_count()}


@router.post("/identity/api-key")
async def issue_key(tenant_id: str = "default"):
    token = identity_service.issue_api_key(tenant_id)
    return {"api_key": token}


@router.post("/evidence/receipt")
async def create_receipt(body: ReceiptRequest):
    r = issue_receipt(body.tenant_id, body.actor, body.capability, body.decision, body.message_id, body.payload)
    return {"receipt_id": r.receipt_id, "chain_hash": r.chain_hash()}


@router.get("/evidence/export/{tenant_id}")
async def export_evidence(tenant_id: str):
    pack = evidence_exporter.export(tenant_id)
    return {"pack_id": pack.pack_id, "receipt_count": len(pack.receipts)}


@router.post("/plugins/register")
async def plugin_register(body: PluginRegisterRequest):
    plugin_registry.register(PluginSpec(name=body.name, version=body.version, risk_tier=body.risk_tier))
    return {"registered": body.name, "risk_tier": body.risk_tier}


@router.post("/plugins/invoke")
async def plugin_invoke(body: PluginInvokeRequest):
    return plugin_registry.invoke(body.name, body.args, confirmed=body.confirmed)


@router.get("/plugins")
async def list_plugins() -> Dict[str, Any]:
    items = {name: {"version": p.version, "risk_tier": p.risk_tier} for name, p in plugin_registry.list().items()}
    return {"plugins": items}


class BiometricRequest(BaseModel):
    hrv: float = 55
    resting_hr: float = 70
    sleep_score: float = 70


@router.post("/biometrics/analyze")
async def biometrics_analyze(body: BiometricRequest):
    analysis = biometric_stress.analyze(body.model_dump())
    return {
        "stress_level": analysis.stress_level,
        "stress_score": analysis.stress_score,
        "components": analysis.components,
        "tone_guidance": analysis.tone_guidance,
    }
