"""Governed Tampa Bay roofing intelligence tasks.

These tasks research and prepare outreach artifacts only. External outreach is
never sent from a Celery task; INITIATE_OUTREACH remains REQUIRE_APPROVAL in
the commercial authority matrix.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .celery_app import celery_app
from src.commerce.authority import CommercialAction, CommercialAuthorityPolicy
from src.commerce.audit import AuditStore

STORAGE_ROOT = Path(os.getenv("SAPHIRA_STORAGE_ROOT", "storage"))
APPROVAL_DIR = STORAGE_ROOT / "data" / "approvals"
APPROVAL_DIR.mkdir(parents=True, exist_ok=True)

policy = CommercialAuthorityPolicy()
audit_store = AuditStore()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_approval(payload: dict[str, Any]) -> str:
    approval_id = str(uuid.uuid4())
    path = APPROVAL_DIR / f"{approval_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return approval_id


@celery_app.task(name="saphira.roofing.research")
def research_roofing_prospect(prospect: dict[str, Any]) -> dict[str, Any]:
    """Normalize a permitted prospect seed and prepare it for qualification."""
    prospect_id = str(prospect.get("id") or uuid.uuid4())
    result = {
        "prospect_id": prospect_id,
        "business_name": prospect.get("business_name", ""),
        "city": prospect.get("city", ""),
        "state": prospect.get("state", "FL"),
        "website": prospect.get("website", ""),
        "source": prospect.get("source", "user_supplied"),
        "status": "RESEARCH_READY",
        "timestamp": _now(),
    }
    audit_store.append(
        actor="saphira.celery",
        action=CommercialAction.RESEARCH_PUBLIC_BUSINESS.value,
        target_type="roofing_prospect",
        target_id=prospect_id,
        policy_decision="ALLOW",
        reason="Public business research is permitted by commercial authority policy",
        resulting_state="RESEARCH_READY",
        executed=True,
    )
    return result


@celery_app.task(name="saphira.roofing.prepare_outreach")
def prepare_roofing_outreach(prospect: dict[str, Any]) -> dict[str, Any]:
    """Generate an outreach-ready artifact and place it behind approval."""
    prospect_id = str(prospect.get("prospect_id") or prospect.get("id") or uuid.uuid4())
    context = {"prospect_id": prospect_id, "channel": prospect.get("channel", "email")}
    decision = policy.authorize(CommercialAction.INITIATE_OUTREACH, context=context)

    approval = {
        "approval_id": None,
        "status": decision.decision.value,
        "prospect": prospect,
        "channel": context["channel"],
        "subject": prospect.get("subject", "Roofing growth opportunity"),
        "draft": prospect.get("draft", ""),
        "policy_reason": decision.reason,
        "created_at": _now(),
    }

    if decision.decision.value == "REQUIRE_APPROVAL":
        approval["approval_id"] = _write_approval(approval)

    audit_store.append(
        actor="saphira.celery",
        action=CommercialAction.INITIATE_OUTREACH.value,
        target_type="roofing_prospect",
        target_id=prospect_id,
        policy_decision=decision.decision.value,
        reason=decision.reason,
        resulting_state="PENDING_REVIEW" if decision.decision.value == "REQUIRE_APPROVAL" else decision.decision.value,
        executed=False,
    )

    return approval


@celery_app.task(name="saphira.roofing.healthcheck")
def roofing_worker_healthcheck() -> dict[str, str]:
    """Lightweight worker health probe."""
    return {"service": "saphira-roofing-worker", "status": "ok", "timestamp": _now()}
