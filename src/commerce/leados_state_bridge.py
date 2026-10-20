"""LeadOS bridge: execution contract + commercial state machine + test-mode checkout.

Test mode never hits live Stripe; records checkout ids only.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.commerce.authority import CommercialAction
from src.commerce.leados_workflow import LeadOSWorkflow, LeadOSConfig, EvidenceStore
from src.commerce.states import CommercialState, CommercialStateMachine
from src.commerce.reserve_entitlements import EntitlementMeter, default_meter, reserve_stage_check
from src.core.execution_contract import ContractDecision


@dataclass
class LeadOSRunResult:
    execution_final: str
    commercial_state: str
    checkout_session_id: str | None
    evidence_id: str | None
    detail: dict[str, Any]


class LeadOSStateBridge:
    def __init__(
        self,
        *,
        workflow: LeadOSWorkflow | None = None,
        meter: EntitlementMeter | None = None,
        test_mode: bool = True,
    ) -> None:
        self.workflow = workflow or LeadOSWorkflow(config=LeadOSConfig())
        self.meter = meter or default_meter
        self.test_mode = test_mode
        self._machines: dict[str, CommercialStateMachine] = {}

    def _machine(self, prospect_id: str) -> CommercialStateMachine:
        if prospect_id not in self._machines:
            self._machines[prospect_id] = CommercialStateMachine(CommercialState.PROSPECT)
        return self._machines[prospect_id]

    def score(self, prospect_id: str, score: float = 0.75) -> LeadOSRunResult:
        ok, reason = reserve_stage_check(estimated_cost_usd=0.02, meter=self.meter)
        if not ok:
            return LeadOSRunResult("DENY", self._machine(prospect_id).state.value, None, None, {"reason": reason})
        ctx = self.workflow.run(
            CommercialAction.SCORE_PROSPECT,
            prospect_id=prospect_id,
            payload={"score": score, "estimated_cost_usd": 0.02, "budget_usd": 10.0},
        )
        if ctx.stages[-1].decision == ContractDecision.SUCCESS:
            self.meter.commit_usage(estimated_cost_usd=0.02)
        return LeadOSRunResult(
            ctx.stages[-1].decision.value,
            self._machine(prospect_id).state.value,
            None,
            ctx.execution_id,
            ctx.result,
        )

    def present_offer(self, prospect_id: str, price_usd: int = 199) -> LeadOSRunResult:
        ctx = self.workflow.run(
            CommercialAction.PRESENT_LEADOS_OFFER,
            prospect_id=prospect_id,
            payload={"price_usd": price_usd, "estimated_cost_usd": 0.01, "budget_usd": 10.0},
        )
        sm = self._machine(prospect_id)
        if ctx.stages[-1].decision == ContractDecision.SUCCESS:
            for target in (
                CommercialState.ENGAGED,
                CommercialState.SALES_CONVERSATION,
                CommercialState.OFFER_PRESENTED,
            ):
                can, _ = sm.can_transition(target)
                if can:
                    try:
                        sm.transition(target)
                    except Exception:
                        break
        return LeadOSRunResult(
            ctx.stages[-1].decision.value,
            sm.state.value,
            None,
            ctx.execution_id,
            ctx.result,
        )

    def create_test_checkout(self, prospect_id: str) -> LeadOSRunResult:
        if not self.test_mode:
            return LeadOSRunResult(
                "DENY",
                self._machine(prospect_id).state.value,
                None,
                None,
                {"reason": "Live checkout disabled in this bridge; use HTTP stripe_checkout with secrets"},
            )
        session_id = f"cs_test_leados_{prospect_id}"
        ctx = self.workflow.run(
            CommercialAction.GENERATE_CHECKOUT,
            prospect_id=prospect_id,
            payload={
                "checkout_session_id": session_id,
                "estimated_cost_usd": 0.01,
                "budget_usd": 10.0,
            },
        )
        sm = self._machine(prospect_id)
        if ctx.stages[-1].decision == ContractDecision.SUCCESS:
            for target in (CommercialState.CHECKOUT_CREATED, CommercialState.PAYMENT_PENDING):
                can, _ = sm.can_transition(target)
                if can:
                    try:
                        sm.transition(target)
                    except Exception:
                        break
        return LeadOSRunResult(
            ctx.stages[-1].decision.value,
            sm.state.value,
            session_id if ctx.stages[-1].decision == ContractDecision.SUCCESS else None,
            ctx.execution_id,
            ctx.result,
        )

    def activate_with_stripe_event(self, prospect_id: str, event_id: str) -> LeadOSRunResult:
        ctx = self.workflow.run(
            CommercialAction.CONFIRM_PAYMENT,
            prospect_id=prospect_id,
            stripe_verified=True,
            stripe_event_id=event_id,
            payload={"estimated_cost_usd": 0.0, "budget_usd": 10.0},
        )
        sm = self._machine(prospect_id)
        if ctx.stages[-1].decision == ContractDecision.SUCCESS:
            can, _ = sm.can_transition(CommercialState.CUSTOMER, stripe_verified=True)
            if can:
                try:
                    sm.transition(CommercialState.CUSTOMER, stripe_verified=True)
                except TypeError:
                    try:
                        sm.transition(CommercialState.CUSTOMER)
                    except Exception:
                        pass
        return LeadOSRunResult(
            ctx.stages[-1].decision.value,
            sm.state.value,
            None,
            ctx.execution_id,
            ctx.result,
        )
