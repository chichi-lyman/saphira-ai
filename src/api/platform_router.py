"""Platform API: autonomy, memory, voice, entitlements, evidence, devices, workflows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
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

from src.orchestration.multi_agent_workflow import (
    MultiAgentWorkflowEngine,
    build_research_code_validate,
    build_analyze_architect_review,
    build_secure_delivery,
    build_custom_linear,
)
from src.orchestration.workers import default_workers
from src.orchestration.executor import TaskExecutor

router = APIRouter(prefix="/platform", tags=["platform"])

# Shared engine instance (workers registered once)
_workflow_engine = MultiAgentWorkflowEngine(
    executor=TaskExecutor(workers=default_workers()),
    entitlements_registry=entitlements,
)


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


class WorkflowRunRequest(BaseModel):
    objective: str
    tenant_id: str = "default"
    template: str = "research_code_validate"  # research_code_validate | analyze_architect_review | secure_delivery | custom
    custom_steps: List[List[str]] = Field(default_factory=list)  # [[name, capability], ...]
    context: Dict[str, Any] = Field(default_factory=dict)


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
    return {
        "tenant_id": ent.tenant_id,
        "plan": ent.plan.name,
        "autonomy_max": ent.plan.autonomy_max,
        "workflow_runs_per_day": ent.plan.workflow_runs_per_day,
        "priority_compute": ent.plan.priority_compute,
    }


@router.get("/entitlements/{tenant_id}")
async def entitlements_usage(tenant_id: str):
    ent = entitlements.get_or_assign(tenant_id)
    return {
        "tenant_id": tenant_id,
        "plan": ent.plan.name,
        "priority_compute": ent.plan.priority_compute,
        "limits": {
            "messages_per_4h": ent.plan.messages_per_4h,
            "deepsearch_per_day": ent.plan.deepsearch_per_day,
            "images_per_day": ent.plan.images_per_day,
            "videos_per_day": ent.plan.videos_per_day,
            "voice_session_mins": ent.plan.voice_session_mins,
            "workflow_runs_per_day": ent.plan.workflow_runs_per_day,
        },
        "usage": {
            "messages_4h": ent.usage.messages_4h,
            "deepsearch_day": ent.usage.deepsearch_day,
            "images_day": ent.usage.images_day,
            "videos_day": ent.usage.videos_day,
            "workflow_runs_day": ent.usage.workflow_runs_day,
            "api_calls": ent.usage.api_calls,
            "agent_minutes": ent.usage.agent_minutes,
        },
        "remaining": {
            "workflow_runs_day": ent.remaining("workflow_runs_day"),
            "deepsearch_day": ent.remaining("deepsearch_day"),
            "messages_4h": ent.remaining("messages_4h"),
        },
    }


@router.get("/entitlements/plans")
async def entitlements_plans():
    plans = entitlements.list_plans()
    return {
        name: {
            "messages_per_4h": p.messages_per_4h,
            "deepsearch_per_day": p.deepsearch_per_day,
            "images_per_day": p.images_per_day,
            "videos_per_day": p.videos_per_day,
            "voice_session_mins": p.voice_session_mins,
            "workflow_runs_per_day": p.workflow_runs_per_day,
            "priority_compute": p.priority_compute,
            "autonomy_max": p.autonomy_max,
        }
        for name, p in plans.items()
    }


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


# ---------------------------------------------------------------------------
# Multi-agent workflows (metered)
# ---------------------------------------------------------------------------

def _serialize_task(task, graph, meter):
    return {
        "task_id": task.id,
        "status": task.status.value,
        "objective": task.objective,
        "errors": task.errors,
        "artifact_count": len(task.artifacts),
        "artifacts": task.artifacts,
        "verification": task.verification,
        "workflow_id": graph.id,
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "capability": n.capability,
                "agent": n.agent,
                "status": n.status.value,
                "error": n.error,
            }
            for n in graph.nodes.values()
        ],
        "metering": meter,
    }


@router.post("/workflows/run")
async def workflow_run(body: WorkflowRunRequest):
    """Run a multi-agent workflow template under tenant metering."""
    template = body.template.strip().lower()
    if template == "research_code_validate":
        task, graph, meter = await _workflow_engine.run_research_code_validate(
            body.objective, context=body.context, tenant_id=body.tenant_id
        )
    elif template == "analyze_architect_review":
        task, graph, meter = await _workflow_engine.run_analyze_architect_review(
            body.objective, context=body.context, tenant_id=body.tenant_id
        )
    elif template == "secure_delivery":
        task, graph, meter = await _workflow_engine.run_secure_delivery(
            body.objective, context=body.context, tenant_id=body.tenant_id
        )
    elif template == "custom":
        steps = [(s[0], s[1]) for s in body.custom_steps if len(s) >= 2]
        if not steps:
            raise HTTPException(status_code=400, detail="custom_steps required for template=custom")
        graph = build_custom_linear(body.objective, steps)
        task, graph, meter = await _workflow_engine.run(
            graph, context=body.context, tenant_id=body.tenant_id
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="template must be research_code_validate | analyze_architect_review | secure_delivery | custom",
        )

    if meter and meter.get("error") == "quota_exceeded":
        raise HTTPException(status_code=429, detail=meter)

    return _serialize_task(task, graph, meter)


@router.post("/workflows/research-code-validate")
async def workflow_rcv(body: WorkflowRunRequest):
    task, graph, meter = await _workflow_engine.run_research_code_validate(
        body.objective, context=body.context, tenant_id=body.tenant_id
    )
    if meter and meter.get("error") == "quota_exceeded":
        raise HTTPException(status_code=429, detail=meter)
    return _serialize_task(task, graph, meter)


@router.post("/workflows/analyze-architect-review")
async def workflow_aar(body: WorkflowRunRequest):
    task, graph, meter = await _workflow_engine.run_analyze_architect_review(
        body.objective, context=body.context, tenant_id=body.tenant_id
    )
    if meter and meter.get("error") == "quota_exceeded":
        raise HTTPException(status_code=429, detail=meter)
    return _serialize_task(task, graph, meter)


@router.post("/workflows/secure-delivery")
async def workflow_secure(body: WorkflowRunRequest):
    task, graph, meter = await _workflow_engine.run_secure_delivery(
        body.objective, context=body.context, tenant_id=body.tenant_id
    )
    if meter and meter.get("error") == "quota_exceeded":
        raise HTTPException(status_code=429, detail=meter)
    return _serialize_task(task, graph, meter)
