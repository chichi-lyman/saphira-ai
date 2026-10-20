"""LeadOS — first complete instrumented, policy-gated business workflow.

LeadOS flow (under the seven-stage execution contract):
  prospect capture → score → (optional) pitch generation → present offer
  → checkout creation → payment pending → (Stripe verified) → customer → active

No external communication is sent by this module. Outreach remains REQUIRE_APPROVAL
or DENY until explicitly enabled under policy. The LLM never owns financial state.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.core.execution_contract import (
    ContractDecision,
    ExecutionContext,
    ExecutionContract,
    Stage,
    StageResult,
)
from src.commerce.authority import (
    CommercialAction,
    CommercialAuthorityPolicy,
    PolicyDecision,
)
from src.commerce.states import CommercialState, CommercialStateMachine
from src.commerce.audit import AuditStore


class EvidenceStore:
    """Append-only evidence for stress-test matrix measurement."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def append(self, evidence: dict[str, Any]) -> None:
        evidence = dict(evidence)
        evidence["recorded_at"] = time.time()
        self._records.append(evidence)

    def all(self) -> list[dict[str, Any]]:
        return list(self._records)

    def by_action(self, action: str) -> list[dict[str, Any]]:
        return [r for r in self._records if r.get("action") == action]

    def success_rate(self, action: str | None = None) -> float:
        rows = self._records if action is None else self.by_action(action)
        if not rows:
            return 0.0
        ok = sum(1 for r in rows if r.get("final_decision") == "SUCCESS")
        return ok / len(rows)

    def avg_elapsed_ms(self, action: str | None = None) -> float:
        rows = self._records if action is None else self.by_action(action)
        if not rows:
            return 0.0
        totals = []
        for r in rows:
            stages = r.get("stages") or []
            totals.append(sum(s.get("elapsed_ms", 0) for s in stages))
        return sum(totals) / len(totals) if totals else 0.0


@dataclass
class LeadOSConfig:
    leados_price_usd: int = 199
    max_retries: int = 3
    require_human_for_outreach: bool = True


class LeadOSWorkflow:
    """Instrumented LeadOS workflow bound to the seven-stage contract + Commerce OS."""

    def __init__(
        self,
        *,
        policy: CommercialAuthorityPolicy | None = None,
        audit: AuditStore | None = None,
        evidence: EvidenceStore | None = None,
        config: LeadOSConfig | None = None,
    ) -> None:
        self.policy = policy or CommercialAuthorityPolicy()
        self.audit = audit or AuditStore()
        self.evidence = evidence or EvidenceStore()
        self.config = config or LeadOSConfig()

    def _validate(self, ctx: ExecutionContext) -> StageResult:
        required = {"prospect_id"}
        missing = required - set(ctx.payload.keys())
        if missing:
            return StageResult(Stage.VALIDATE, ContractDecision.DENY, f"Missing required fields: {sorted(missing)}")
        if ctx.action == CommercialAction.PRESENT_LEADOS_OFFER.value:
            price = ctx.payload.get("price_usd", self.config.leados_price_usd)
            if int(price) not in (199, 500):
                return StageResult(Stage.VALIDATE, ContractDecision.DENY, f"Out-of-policy LeadOS price: {price}")
        ctx.estimated_cost_usd = float(ctx.payload.get("estimated_cost_usd") or 0.05)
        return StageResult(Stage.VALIDATE, ContractDecision.CONTINUE, "LeadOS payload validated")

    def _authorize(self, ctx: ExecutionContext) -> StageResult:
        action = ctx.action
        try:
            ca = CommercialAction(action)
        except ValueError:
            return StageResult(Stage.AUTHORIZE, ContractDecision.DENY, f"Unknown action: {action}")

        context = {
            "price_usd": ctx.payload.get("price_usd", self.config.leados_price_usd),
            "stripe_verified": ctx.stripe_verified,
            "stripe_event_id": ctx.stripe_event_id,
            **ctx.payload,
        }
        result = self.policy.evaluate(ca, context=context)
        ctx.policy_decision = result.decision.value

        if result.decision is PolicyDecision.DENY:
            return StageResult(Stage.AUTHORIZE, ContractDecision.DENY, result.reason, {"policy": result.decision.value})
        if result.decision is PolicyDecision.REQUIRE_APPROVAL:
            return StageResult(Stage.AUTHORIZE, ContractDecision.REQUIRE_APPROVAL, result.reason, {"policy": result.decision.value})
        return StageResult(Stage.AUTHORIZE, ContractDecision.CONTINUE, result.reason, {"policy": result.decision.value})

    def _reserve(self, ctx: ExecutionContext) -> StageResult:
        budget = float(ctx.payload.get("budget_usd") or 10.0)
        if ctx.estimated_cost_usd > budget:
            return StageResult(Stage.RESERVE, ContractDecision.DENY, f"Estimated cost {ctx.estimated_cost_usd} exceeds budget {budget}")
        ctx.reserved_budget_usd = ctx.estimated_cost_usd
        return StageResult(Stage.RESERVE, ContractDecision.CONTINUE, f"Reserved ${ctx.reserved_budget_usd:.4f}")

    def _execute(self, ctx: ExecutionContext) -> StageResult:
        action = ctx.action
        payload = ctx.payload

        if action == CommercialAction.SCORE_PROSPECT.value:
            score = float(payload.get("score") or 0.7)
            ctx.result = {"prospect_id": payload["prospect_id"], "score": score, "qualified": score >= 0.6}
            return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, "Prospect scored", ctx.result)

        if action == CommercialAction.GENERATE_PITCH.value:
            ctx.result = {
                "prospect_id": payload["prospect_id"],
                "pitch_draft": payload.get("pitch_draft") or f"LeadOS proposal for {payload['prospect_id']}",
                "status": "draft_only",
            }
            return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, "Pitch draft generated (not sent)", ctx.result)

        if action == CommercialAction.PRESENT_LEADOS_OFFER.value:
            price = int(payload.get("price_usd") or self.config.leados_price_usd)
            ctx.result = {
                "prospect_id": payload["prospect_id"],
                "offer": "Saphira LeadOS",
                "price_usd": price,
                "status": "offer_recorded",
            }
            return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, "LeadOS offer recorded", ctx.result)

        if action == CommercialAction.GENERATE_CHECKOUT.value:
            ctx.result = {
                "prospect_id": payload["prospect_id"],
                "checkout_session_id": payload.get("checkout_session_id") or f"cs_test_{payload['prospect_id']}",
                "status": "checkout_created_test",
            }
            return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, "Checkout session recorded (test)", ctx.result)

        if action in (CommercialAction.CONFIRM_PAYMENT.value, CommercialAction.ACTIVATE_SUBSCRIPTION.value):
            if not ctx.stripe_verified:
                return StageResult(Stage.EXECUTE, ContractDecision.DENY, "Payment confirmation requires verified Stripe event")
            ctx.result = {
                "prospect_id": payload["prospect_id"],
                "stripe_event_id": ctx.stripe_event_id,
                "status": "customer_activated",
            }
            return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, "Subscription activated via verified Stripe event", ctx.result)

        if action == CommercialAction.INITIATE_OUTREACH.value:
            return StageResult(
                Stage.EXECUTE,
                ContractDecision.REQUIRE_APPROVAL,
                "Outreach requires explicit human approval; no message sent",
                {"sent": False},
            )

        ctx.result = {"prospect_id": payload.get("prospect_id"), "action": action, "status": "recorded"}
        return StageResult(Stage.EXECUTE, ContractDecision.SUCCESS, f"Action {action} recorded without external side-effect", ctx.result)

    def _verify(self, ctx: ExecutionContext) -> StageResult:
        if not ctx.result:
            return StageResult(Stage.VERIFY, ContractDecision.FAIL, "No result to verify")
        if ctx.action in (CommercialAction.CONFIRM_PAYMENT.value, CommercialAction.ACTIVATE_SUBSCRIPTION.value):
            if not ctx.stripe_verified or not ctx.stripe_event_id:
                return StageResult(Stage.VERIFY, ContractDecision.FAIL, "Payment path missing Stripe verification evidence")
        return StageResult(Stage.VERIFY, ContractDecision.CONTINUE, "Result structure verified")

    def run(
        self,
        action: str | CommercialAction,
        *,
        prospect_id: str,
        actor: str = "saphira",
        tenant_id: str | None = None,
        user_id: str | None = None,
        payload: dict[str, Any] | None = None,
        stripe_verified: bool = False,
        stripe_event_id: str | None = None,
    ) -> ExecutionContext:
        if isinstance(action, CommercialAction):
            action = action.value

        ctx = ExecutionContext(
            actor=actor,
            action=action,
            tenant_id=tenant_id,
            user_id=user_id,
            payload={"prospect_id": prospect_id, **(payload or {})},
            stripe_verified=stripe_verified,
            stripe_event_id=stripe_event_id,
        )

        contract = ExecutionContract(
            validate_fn=self._validate,
            authorize_fn=self._authorize,
            reserve_fn=self._reserve,
            execute_fn=self._execute,
            verify_fn=self._verify,
            max_retries=self.config.max_retries,
        )
        result_ctx = contract.run(ctx)
        self.evidence.append(result_ctx.to_evidence())

        try:
            self.audit.append(
                actor=actor,
                action=action,
                target_type="prospect",
                target_id=prospect_id,
                policy_decision=result_ctx.policy_decision or "UNKNOWN",
                reason=result_ctx.stages[-1].reason if result_ctx.stages else "",
                previous_state="",
                resulting_state="",
                event_id=stripe_event_id or "",
                metadata={
                    "execution_id": result_ctx.execution_id,
                    "final_decision": result_ctx.stages[-1].decision.value if result_ctx.stages else None,
                },
                executed=result_ctx.stages[-1].decision.value == "SUCCESS" if result_ctx.stages else False,
            )
        except Exception:
            pass

        return result_ctx


def matrix_snapshot(evidence: EvidenceStore) -> dict[str, Any]:
    """Produce a minimal stress-test matrix snapshot from collected evidence."""
    rows = evidence.all()
    return {
        "total_executions": len(rows),
        "success_rate": evidence.success_rate(),
        "avg_elapsed_ms": evidence.avg_elapsed_ms(),
        "by_action": {
            action: {
                "count": len(evidence.by_action(action)),
                "success_rate": evidence.success_rate(action),
                "avg_elapsed_ms": evidence.avg_elapsed_ms(action),
            }
            for action in sorted({r.get("action") for r in rows if r.get("action")})
        },
        "policy_denials": sum(1 for r in rows if r.get("final_decision") == "DENY"),
        "require_approval": sum(1 for r in rows if r.get("final_decision") == "REQUIRE_APPROVAL"),
        "failures": sum(1 for r in rows if r.get("final_decision") == "FAIL"),
        "successes": sum(1 for r in rows if r.get("final_decision") == "SUCCESS"),
    }
