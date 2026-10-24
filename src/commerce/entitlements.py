# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Entitlement service — maps Stripe plans / tenant status to usage limits.
# Used by orchestrator and capability registry as a pre-flight gate.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger("saphira.entitlements")


class Plan(str, Enum):
    FREEMIUM = "freemium"
    PRO = "pro"
    ULTRA = "ultra"


@dataclass(frozen=True)
class PlanLimits:
    messages_per_4h: int
    deepsearch_per_day: int
    images_per_day: int
    voice_minutes: int
    max_memory_items: int
    priority: int  # higher = preferred scheduling


# Defaults aligned with Super Saphira tier table in README
PLAN_LIMITS: dict[Plan, PlanLimits] = {
    Plan.FREEMIUM: PlanLimits(
        messages_per_4h=40,
        deepsearch_per_day=5,
        images_per_day=20,
        voice_minutes=10,
        max_memory_items=200,
        priority=1,
    ),
    Plan.PRO: PlanLimits(
        messages_per_4h=150,
        deepsearch_per_day=50,
        images_per_day=200,
        voice_minutes=30,
        max_memory_items=2000,
        priority=5,
    ),
    Plan.ULTRA: PlanLimits(
        messages_per_4h=250,
        deepsearch_per_day=200,
        images_per_day=500,
        voice_minutes=60,
        max_memory_items=10000,
        priority=10,
    ),
}


class EntitlementService:
    """Simple in-memory / future-DB backed entitlement lookup.

    In production this should read from the same store that Stripe webhooks update.
    """

    def __init__(self):
        # tenant_id → Plan
        self._tenant_plans: dict[str, Plan] = {}

    def set_plan(self, tenant_id: str, plan: Plan) -> None:
        self._tenant_plans[tenant_id] = plan
        logger.info("Tenant %s plan set to %s", tenant_id, plan.value)

    def get_plan(self, tenant_id: str) -> Plan:
        return self._tenant_plans.get(tenant_id, Plan.FREEMIUM)

    def get_limits(self, tenant_id: str) -> PlanLimits:
        plan = self.get_plan(tenant_id)
        return PLAN_LIMITS[plan]

    def check(self, tenant_id: str, resource: str, current_usage: int) -> bool:
        """Return True if the tenant is still within quota for the resource."""
        limits = self.get_limits(tenant_id)
        mapping = {
            "messages": limits.messages_per_4h,
            "deepsearch": limits.deepsearch_per_day,
            "images": limits.images_per_day,
            "voice_minutes": limits.voice_minutes,
            "memory_items": limits.max_memory_items,
        }
        ceiling = mapping.get(resource)
        if ceiling is None:
            logger.warning("Unknown resource checked: %s", resource)
            return True
        return current_usage < ceiling


# Module-level singleton for easy import
entitlements = EntitlementService()
