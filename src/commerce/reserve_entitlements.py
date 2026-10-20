"""RESERVE-stage entitlements metering for the execution contract.

Blocks EXECUTE when plan limits are exhausted.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UsageCounters:
    workflow_runs_day: int = 0
    api_calls: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class PlanLimits:
    workflow_runs_day: int = 100
    api_calls_monthly: int = 10_000
    max_cost_usd_day: float = 50.0


@dataclass
class EntitlementMeter:
    plan: PlanLimits = field(default_factory=PlanLimits)
    usage: UsageCounters = field(default_factory=UsageCounters)

    def remaining_workflows(self) -> int:
        return max(0, self.plan.workflow_runs_day - self.usage.workflow_runs_day)

    def remaining_cost(self) -> float:
        return max(0.0, self.plan.max_cost_usd_day - self.usage.estimated_cost_usd)

    def can_reserve(self, *, estimated_cost_usd: float = 0.0, workflows: int = 1) -> tuple[bool, str]:
        if self.remaining_workflows() < workflows:
            return False, f"Workflow quota exhausted ({self.usage.workflow_runs_day}/{self.plan.workflow_runs_day})"
        if estimated_cost_usd > self.remaining_cost():
            return False, f"Daily cost budget exceeded (need {estimated_cost_usd}, left {self.remaining_cost():.4f})"
        return True, "Reservation permitted"

    def commit_usage(self, *, estimated_cost_usd: float = 0.0, workflows: int = 1) -> None:
        self.usage.workflow_runs_day += workflows
        self.usage.estimated_cost_usd += estimated_cost_usd
        self.usage.api_calls += 1


default_meter = EntitlementMeter()


def reserve_stage_check(
    *,
    estimated_cost_usd: float,
    meter: EntitlementMeter | None = None,
) -> tuple[bool, str]:
    m = meter or default_meter
    return m.can_reserve(estimated_cost_usd=estimated_cost_usd)
