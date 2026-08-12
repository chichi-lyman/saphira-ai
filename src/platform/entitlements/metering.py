"""Metered SaaS entitlements and quota enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class EntitlementPlan:
    name: str
    api_calls_monthly: int = 10_000
    agent_minutes_monthly: int = 600
    seats: int = 1
    autonomy_max: str = "L2_supervised"


@dataclass
class UsageCounters:
    api_calls: int = 0
    agent_minutes: float = 0.0
    seats_used: int = 0


@dataclass
class TenantEntitlements:
    tenant_id: str
    plan: EntitlementPlan
    usage: UsageCounters = field(default_factory=UsageCounters)

    def check(self, metric: str, amount: float = 1.0) -> bool:
        if metric == "api_calls":
            return self.usage.api_calls + amount <= self.plan.api_calls_monthly
        if metric == "agent_minutes":
            return self.usage.agent_minutes + amount <= self.plan.agent_minutes_monthly
        if metric == "seats":
            return self.usage.seats_used + amount <= self.plan.seats
        return False

    def consume(self, metric: str, amount: float = 1.0) -> bool:
        if not self.check(metric, amount):
            return False
        if metric == "api_calls":
            self.usage.api_calls += int(amount)
        elif metric == "agent_minutes":
            self.usage.agent_minutes += amount
        elif metric == "seats":
            self.usage.seats_used += int(amount)
        return True


class EntitlementRegistry:
    def __init__(self) -> None:
        self._tenants: Dict[str, TenantEntitlements] = {}
        self._plans = {
            "free": EntitlementPlan("free", 1_000, 60, 1, "L1_confirm_first"),
            "pro": EntitlementPlan("pro", 50_000, 2_000, 5, "L2_supervised"),
            "enterprise": EntitlementPlan("enterprise", 1_000_000, 50_000, 100, "L3_background"),
        }

    def assign(self, tenant_id: str, plan_name: str = "free") -> TenantEntitlements:
        plan = self._plans.get(plan_name, self._plans["free"])
        ent = TenantEntitlements(tenant_id=tenant_id, plan=plan)
        self._tenants[tenant_id] = ent
        return ent

    def get(self, tenant_id: str) -> Optional[TenantEntitlements]:
        return self._tenants.get(tenant_id)


entitlements = EntitlementRegistry()
