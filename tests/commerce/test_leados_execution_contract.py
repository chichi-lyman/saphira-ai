"""Tests for seven-stage execution contract + LeadOS workflow.

These tests supply evidence that:
  - DENY / REQUIRE_APPROVAL never execute side-effects
  - Payment activation requires stripe_verified
  - Outreach is gated
  - Evidence is recorded for matrix measurement
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

from src.core.execution_contract import (
    ContractDecision,
    ExecutionContext,
    ExecutionContract,
    Stage,
    StageResult,
)
from src.commerce.leados_workflow import LeadOSWorkflow, LeadOSConfig, EvidenceStore, matrix_snapshot
from src.commerce.authority import CommercialAction, CommercialAuthorityPolicy, PolicyDecision


@pytest.fixture
def workflow():
    return LeadOSWorkflow(
        policy=CommercialAuthorityPolicy(),
        evidence=EvidenceStore(),
        config=LeadOSConfig(leados_price_usd=199),
    )


def test_score_prospect_success(workflow):
    ctx = workflow.run(
        CommercialAction.SCORE_PROSPECT,
        prospect_id="p-001",
        payload={"score": 0.82},
    )
    assert ctx.stages[-1].decision == ContractDecision.SUCCESS
    assert ctx.result["qualified"] is True
    assert len(workflow.evidence.all()) == 1


def test_present_offer_in_policy(workflow):
    ctx = workflow.run(
        CommercialAction.PRESENT_LEADOS_OFFER,
        prospect_id="p-002",
        payload={"price_usd": 199},
    )
    assert ctx.stages[-1].decision == ContractDecision.SUCCESS
    assert ctx.result["price_usd"] == 199


def test_present_offer_out_of_policy_denied(workflow):
    ctx = workflow.run(
        CommercialAction.PRESENT_LEADOS_OFFER,
        prospect_id="p-003",
        payload={"price_usd": 49},
    )
    assert ctx.stages[-1].decision in (ContractDecision.DENY, ContractDecision.REQUIRE_APPROVAL)


def test_payment_without_stripe_denied(workflow):
    ctx = workflow.run(
        CommercialAction.CONFIRM_PAYMENT,
        prospect_id="p-004",
        stripe_verified=False,
    )
    assert ctx.stages[-1].decision in (ContractDecision.DENY, ContractDecision.FAIL)
    assert not any(s.stage == Stage.COMMIT and s.decision == ContractDecision.SUCCESS for s in ctx.stages)


def test_payment_with_stripe_verified_succeeds(workflow):
    ctx = workflow.run(
        CommercialAction.CONFIRM_PAYMENT,
        prospect_id="p-005",
        stripe_verified=True,
        stripe_event_id="evt_test_123",
    )
    assert ctx.stages[-1].decision == ContractDecision.SUCCESS
    assert ctx.result["status"] == "customer_activated"


def test_outreach_requires_approval(workflow):
    ctx = workflow.run(
        CommercialAction.INITIATE_OUTREACH,
        prospect_id="p-006",
    )
    final = ctx.stages[-1].decision
    assert final in (ContractDecision.REQUIRE_APPROVAL, ContractDecision.DENY)
    assert ctx.result.get("sent") is not True


def test_matrix_snapshot_populated(workflow):
    workflow.run(CommercialAction.SCORE_PROSPECT, prospect_id="m-1", payload={"score": 0.9})
    workflow.run(CommercialAction.INITIATE_OUTREACH, prospect_id="m-2")
    workflow.run(
        CommercialAction.CONFIRM_PAYMENT,
        prospect_id="m-3",
        stripe_verified=True,
        stripe_event_id="evt_m",
    )
    snap = matrix_snapshot(workflow.evidence)
    assert snap["total_executions"] == 3
    assert "success_rate" in snap
    assert snap["successes"] >= 1
    assert snap["require_approval"] + snap["policy_denials"] + snap["failures"] + snap["successes"] == 3


def test_seven_stages_order_on_success(workflow):
    ctx = workflow.run(
        CommercialAction.SCORE_PROSPECT,
        prospect_id="order-1",
        payload={"score": 0.75},
    )
    stage_names = [s.stage.value for s in ctx.stages]
    assert stage_names[0] == "PROPOSE"
    assert stage_names[-1] == "COMMIT"
    assert "VALIDATE" in stage_names
    assert "AUTHORIZE" in stage_names
    assert "RESERVE" in stage_names
    assert "EXECUTE" in stage_names
    assert "VERIFY" in stage_names


def test_execution_contract_standalone_deny():
    def deny_auth(ctx: ExecutionContext) -> StageResult:
        return StageResult(Stage.AUTHORIZE, ContractDecision.DENY, "blocked")

    contract = ExecutionContract(authorize_fn=deny_auth)
    ctx = ExecutionContext(action="test")
    out = contract.run(ctx)
    assert out.stages[-1].decision == ContractDecision.DENY
    assert out.stages[-1].stage == Stage.ROLLBACK
