# Copyright © 2026 Chelsea Megan Woods
# Shared multi-agent handoff envelope (aligned with novaaethrea-agent schemas)

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone


def make_envelope(
    *,
    from_agent: str,
    to_agent: str,
    objective: str,
    policy: str = "ALLOW",
    constraints: Optional[List[str]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    context_pack: Optional[Dict[str, Any]] = None,
    deadline_ms: Optional[int] = None,
    trace_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "trace_id": trace_id or str(uuid.uuid4()),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "task_id": task_id or str(uuid.uuid4()),
        "objective": objective,
        "constraints": constraints or [],
        "inputs": inputs or {},
        "context_pack": context_pack,
        "policy": policy,
        "deadline_ms": deadline_ms,
        "reply_channel": "orchestrator",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


STATUS_ACCEPTED = "ACCEPTED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_NEED_INPUT = "NEED_INPUT"
STATUS_NEED_APPROVAL = "NEED_APPROVAL"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_ESCALATED = "ESCALATED"
