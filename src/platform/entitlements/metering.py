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
    # Super Saphira surface quotas (rolling / daily where applicable)
    messages_per_4h: int = 50
    deepsearch_per_day: int = 10
    images_per_day: int = 50
    videos_per_day: int = 10
    voice_session_mins: int = 15
    priority_compute: bool = False
    workflow_runs_per_day: int = 20


@dataclass
class UsageCounters:
    api_calls: int = 0
    agent_minutes: float = 0.0
    seats_used: int = 0
    messages_4h: int = 0
    deepsearch_day: int = 0
    images_day: int = 0
    videos_day: int = 0
    workflow_runs_day: int = 0


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
        if metric == "messages_4h":
            return self.usage.messages_4h + amount <= self.plan.messages_per_4h
        if metric == "deepsearch_day":
            return self.usage.deepsearch_day + amount <= self.plan.deepsearch_per_day
        if metric == "images_day":
            return self.usage.images_day + amount <= self.plan.images_per_day
        if metric == "videos_day":
            return self.usage.videos_day + amount <= self.plan.videos_per_day
        if metric == "workflow_runs_day":
            return self.usage.workflow_runs_day + amount <= self.plan.workflow_runs_per_day
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
        elif metric == "messages_4h":
            self.usage.messages_4h += int(amount)
        elif metric == "deepsearch_day":
            self.usage.deepsearch_day += int(amount)
        elif metric == "images_day":
            self.usage.images_day += int(amount)
        elif metric == "videos_day":
            self.usage.videos_day += int(amount)
        elif metric == "workflow_runs_day":
            self.usage.workflow_runs_day += int(amount)
        return True

    def remaining(self, metric: str) -> float:
        if metric == "workflow_runs_day":
            return max(0, self.plan.workflow_runs_per_day - self.usage.workflow_runs_day)
        if metric == "deepsearch_day":
            return max(0, self.plan.deepsearch_per_day - self.usage.deepsearch_day)
        if metric == "messages_4h":
            return max(0, self.plan.messages_per_4h - self.usage.messages_4h)
        if metric == "images_day":
            return max(0, self.plan.images_per_day - self.usage.images_day)
        if metric == "videos_day":
            return max(0, self.plan.videos_per_day - self.usage.videos_day)
        if metric == "api_calls":
            return max(0, self.plan.api_calls_monthly - self.usage.api_calls)
        if metric == "agent_minutes":
            return max(0.0, self.plan.agent_minutes_monthly - self.usage.agent_minutes)
        return 0.0


class EntitlementRegistry:
    def __init__(self) -> None:
        self._tenants: Dict[str, TenantEntitlements] = {}
        self._plans = {
            "free": EntitlementPlan(
                "free",
                api_calls_monthly=1_000,
                agent_minutes_monthly=60,
                seats=1,
                autonomy_max="L1_confirm_first",
                messages_per_4h=40,
                deepsearch_per_day=5,
                images_per_day=20,
                videos_per_day=5,
                voice_session_mins=10,
                priority_compute=False,
                workflow_runs_per_day=10,
            ),
            "pro": EntitlementPlan(
                "pro",
                api_calls_monthly=50_000,
                agent_minutes_monthly=2_000,
                seats=5,
                autonomy_max="L2_supervised",
                messages_per_4h=80,
                deepsearch_per_day=20,
                images_per_day=100,
                videos_per_day=25,
                voice_session_mins=20,
                priority_compute=False,
                workflow_runs_per_day=50,
            ),
            "super_saphira": EntitlementPlan(
                "super_saphira",
                api_calls_monthly=200_000,
                agent_minutes_monthly=10_000,
                seats=10,
                autonomy_max="L2_supervised",
                messages_per_4h=150,
                deepsearch_per_day=50,
                images_per_day=200,
                videos_per_day=50,
                voice_session_mins=30,
                priority_compute=False,
                workflow_runs_per_day=200,
            ),
            "super_saphira_heavy": EntitlementPlan(
                "super_saphira_heavy",
                api_calls_monthly=1_000_000,
                agent_minutes_monthly=50_000,
                seats=50,
                autonomy_max="L3_background",
                messages_per_4h=250,
                deepsearch_per_day=200,
                images_per_day=500,
                videos_per_day=150,
                voice_session_mins=60,
                priority_compute=True,
                workflow_runs_per_day=1_000,
            ),
            "enterprise": EntitlementPlan(
                "enterprise",
                api_calls_monthly=1_000_000,
                agent_minutes_monthly=50_000,
                seats=100,
                autonomy_max="L3_background",
                messages_per_4h=500,
                deepsearch_per_day=500,
                images_per_day=1_000,
                videos_per_day=300,
                voice_session_mins=120,
                priority_compute=True,
                workflow_runs_per_day=5_000,
            ),
        }

    def assign(self, tenant_id: str, plan_name: str = "free") -> TenantEntitlements:
        plan = self._plans.get(plan_name, self._plans["free"])
        ent = TenantEntitlements(tenant_id=tenant_id, plan=plan)
        self._tenants[tenant_id] = ent
        return ent

    def get(self, tenant_id: str) -> Optional[TenantEntitlements]:
        return self._tenants.get(tenant_id)

    def get_or_assign(self, tenant_id: str, plan_name: str = "free") -> TenantEntitlements:
        existing = self._tenants.get(tenant_id)
        if existing:
            return existing
        return self.assign(tenant_id, plan_name)

    def list_plans(self) -> Dict[str, EntitlementPlan]:
        return dict(self._plans)

    def enforce(self, tenant_id: str, metric: str, amount: float = 1.0) -> tuple[bool, Optional[TenantEntitlements], str]:
        """Check + consume. Returns (ok, entitlements, reason)."""
        ent = self.get_or_assign(tenant_id)
        if not ent.check(metric, amount):
            return (
                False,
                ent,
                f"quota_exceeded:{metric}:plan={ent.plan.name}:limit={getattr(ent.plan, metric.replace('_day', '_per_day').replace('messages_4h', 'messages_per_4h'), '?')}",
            )
        ent.consume(metric, amount)
        return True, ent, "ok"


entitlements = EntitlementRegistry()
