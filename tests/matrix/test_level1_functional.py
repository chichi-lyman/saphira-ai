"""Matrix Level-1 — Functional stress-test suite.

Valid inputs, ordinary tasks, correct policy outcomes.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

from src.commerce.leados_workflow import LeadOSWorkflow, EvidenceStore, matrix_snapshot
from src.commerce.authority import CommercialAction
from src.commerce.reserve_entitlements import EntitlementMeter, PlanLimits, UsageCounters
from src.core.execution_contract import ContractDecision
from src.core.provider_router import ProviderModelRouter
from src.providers.registry import ProviderRegistry
from src.platform.memory.tenant_guard import TenantMemoryGuard, MissingTenantError
from src.platform.memory.hybrid import TenantMemoryStore


def test_level1_score_success():
    wf = LeadOSWorkflow(evidence=EvidenceStore())
    ctx = wf.run(CommercialAction.SCORE_PROSPECT, prospect_id="L1-1", payload={"score": 0.8})
    assert ctx.stages[-1].decision == ContractDecision.SUCCESS


def test_level1_outreach_gated():
    wf = LeadOSWorkflow(evidence=EvidenceStore())
    ctx = wf.run(CommercialAction.INITIATE_OUTREACH, prospect_id="L1-2")
    assert ctx.stages[-1].decision in (ContractDecision.REQUIRE_APPROVAL, ContractDecision.DENY)


def test_level1_payment_requires_stripe():
    wf = LeadOSWorkflow(evidence=EvidenceStore())
    ctx = wf.run(CommercialAction.CONFIRM_PAYMENT, prospect_id="L1-3", stripe_verified=False)
    assert ctx.stages[-1].decision in (ContractDecision.DENY, ContractDecision.FAIL)


def test_level1_matrix_snapshot_shape():
    ev = EvidenceStore()
    wf = LeadOSWorkflow(evidence=ev)
    wf.run(CommercialAction.SCORE_PROSPECT, prospect_id="L1-4", payload={"score": 0.9})
    snap = matrix_snapshot(ev)
    assert snap["total_executions"] >= 1
    assert "success_rate" in snap
    assert "by_action" in snap


def test_level1_tenant_memory_required():
    g = TenantMemoryGuard(store=TenantMemoryStore())
    with pytest.raises(MissingTenantError):
        g.add(tenant_id=None, user_id="u", content="x")


def test_level1_entitlement_blocks_when_exhausted():
    meter = EntitlementMeter(
        plan=PlanLimits(workflow_runs_day=1, max_cost_usd_day=1.0),
        usage=UsageCounters(workflow_runs_day=1, estimated_cost_usd=0.0),
    )
    ok, reason = meter.can_reserve(estimated_cost_usd=0.01)
    assert ok is False
    assert "exhausted" in reason.lower() or "quota" in reason.lower()


def test_level1_provider_router_status():
    r = ProviderModelRouter(ProviderRegistry())
    status = r.status()
    assert "openai_primary" in status or "gemini_primary" in status
    decision = r.choose(require_capability="chat")
    assert decision.reason
