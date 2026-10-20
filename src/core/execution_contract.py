"""Seven-stage execution contract for all consequential Saphira / Nova Umbrella actions.

Stages (mandatory order):
  1. PROPOSE   — create a structured task
  2. VALIDATE  — check inputs, scope, expected cost
  3. AUTHORIZE — identity, permissions, approval rules
  4. RESERVE   — usage and spending limits
  5. EXECUTE   — run the model or workflow
  6. VERIFY    — validate results and side effects
  7. COMMIT or ROLLBACK — record outcome and recover safely

Critical rules:
  - DENY and REQUIRE_APPROVAL never execute.
  - External side-effects (payments, messages, deploys) require explicit authorization.
  - Every stage produces an evidence record.
  - Bounded retries only; no uncontrolled recursion.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional


class Stage(str, Enum):
    PROPOSE = "PROPOSE"
    VALIDATE = "VALIDATE"
    AUTHORIZE = "AUTHORIZE"
    RESERVE = "RESERVE"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"


class ContractDecision(str, Enum):
    CONTINUE = "CONTINUE"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    FAIL = "FAIL"
    SUCCESS = "SUCCESS"


@dataclass
class StageResult:
    stage: Stage
    decision: ContractDecision
    reason: str
    data: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExecutionContext:
    """Mutable context carried through all stages."""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor: str = "saphira"
    action: str = ""
    tenant_id: str | None = None
    user_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    reserved_budget_usd: float = 0.0
    policy_decision: str | None = None
    stripe_verified: bool = False
    stripe_event_id: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    stages: list[StageResult] = field(default_factory=list)

    def record(self, stage: Stage, decision: ContractDecision, reason: str, data: dict | None = None, elapsed_ms: float = 0.0) -> StageResult:
        sr = StageResult(stage=stage, decision=decision, reason=reason, data=dict(data or {}), elapsed_ms=elapsed_ms)
        self.stages.append(sr)
        return sr

    def to_evidence(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "actor": self.actor,
            "action": self.action,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "estimated_cost_usd": self.estimated_cost_usd,
            "reserved_budget_usd": self.reserved_budget_usd,
            "policy_decision": self.policy_decision,
            "stripe_verified": self.stripe_verified,
            "stripe_event_id": self.stripe_event_id,
            "result": self.result,
            "metadata": self.metadata,
            "stages": [asdict(s) for s in self.stages],
            "final_decision": self.stages[-1].decision.value if self.stages else None,
        }


StageHandler = Callable[[ExecutionContext], StageResult]


class ExecutionContract:
    """Runs the seven-stage contract. Handlers can be overridden per domain."""

    def __init__(
        self,
        *,
        validate_fn: StageHandler | None = None,
        authorize_fn: StageHandler | None = None,
        reserve_fn: StageHandler | None = None,
        execute_fn: StageHandler | None = None,
        verify_fn: StageHandler | None = None,
        max_retries: int = 3,
    ) -> None:
        self.validate_fn = validate_fn
        self.authorize_fn = authorize_fn
        self.reserve_fn = reserve_fn
        self.execute_fn = execute_fn
        self.verify_fn = verify_fn
        self.max_retries = max_retries

    def _run_stage(self, stage: Stage, ctx: ExecutionContext, handler: StageHandler | None, default_ok_reason: str) -> StageResult:
        t0 = time.perf_counter()
        if handler is None:
            sr = ctx.record(stage, ContractDecision.CONTINUE, default_ok_reason, elapsed_ms=(time.perf_counter() - t0) * 1000)
            return sr
        try:
            sr = handler(ctx)
            sr.elapsed_ms = (time.perf_counter() - t0) * 1000
            if not any(s.stage == stage for s in ctx.stages):
                ctx.stages.append(sr)
            return sr
        except Exception as e:
            return ctx.record(stage, ContractDecision.FAIL, f"{stage.value} raised: {e}", elapsed_ms=(time.perf_counter() - t0) * 1000)

    def run(self, ctx: ExecutionContext) -> ExecutionContext:
        ctx.record(Stage.PROPOSE, ContractDecision.CONTINUE, f"Task proposed: {ctx.action}", {"payload_keys": list(ctx.payload.keys())})

        sr = self._run_stage(Stage.VALIDATE, ctx, self.validate_fn, "Inputs and scope accepted")
        if sr.decision in (ContractDecision.DENY, ContractDecision.FAIL, ContractDecision.REQUIRE_APPROVAL):
            ctx.record(Stage.ROLLBACK, ContractDecision.DENY if sr.decision != ContractDecision.FAIL else ContractDecision.FAIL, f"Stopped at VALIDATE: {sr.reason}")
            return ctx

        sr = self._run_stage(Stage.AUTHORIZE, ctx, self.authorize_fn, "Authorization granted")
        ctx.policy_decision = sr.decision.value
        if sr.decision == ContractDecision.REQUIRE_APPROVAL:
            ctx.record(Stage.ROLLBACK, ContractDecision.REQUIRE_APPROVAL, f"Requires approval: {sr.reason}")
            return ctx
        if sr.decision in (ContractDecision.DENY, ContractDecision.FAIL):
            ctx.record(Stage.ROLLBACK, sr.decision, f"Stopped at AUTHORIZE: {sr.reason}")
            return ctx

        sr = self._run_stage(Stage.RESERVE, ctx, self.reserve_fn, "Budget reserved")
        if sr.decision in (ContractDecision.DENY, ContractDecision.FAIL, ContractDecision.REQUIRE_APPROVAL):
            ctx.record(Stage.ROLLBACK, sr.decision, f"Stopped at RESERVE: {sr.reason}")
            return ctx

        last_exec: StageResult | None = None
        for attempt in range(1, self.max_retries + 1):
            sr = self._run_stage(Stage.EXECUTE, ctx, self.execute_fn, f"Executed (attempt {attempt})")
            last_exec = sr
            if sr.decision in (ContractDecision.CONTINUE, ContractDecision.SUCCESS):
                break
            if sr.decision in (ContractDecision.DENY, ContractDecision.REQUIRE_APPROVAL):
                break

        if last_exec and last_exec.decision not in (ContractDecision.CONTINUE, ContractDecision.SUCCESS):
            ctx.record(Stage.ROLLBACK, ContractDecision.FAIL, f"Execute failed after retries: {last_exec.reason}")
            return ctx

        sr = self._run_stage(Stage.VERIFY, ctx, self.verify_fn, "Results verified")
        if sr.decision in (ContractDecision.DENY, ContractDecision.FAIL):
            ctx.record(Stage.ROLLBACK, ContractDecision.FAIL, f"Verify failed: {sr.reason}")
            return ctx

        ctx.record(Stage.COMMIT, ContractDecision.SUCCESS, "Outcome committed", {"result_keys": list(ctx.result.keys())})
        return ctx
