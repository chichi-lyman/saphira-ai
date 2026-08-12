"""Cryptographic-style action receipts for high-impact agent actions."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass
class ActionReceipt:
    receipt_id: str
    tenant_id: str
    actor: str
    capability: str
    policy_decision: str
    model_version: str
    input_hash: str
    created_at: float
    metadata: Dict[str, Any]
    def chain_hash(self, previous: Optional[str] = None) -> str:
        payload = json.dumps(asdict(self), sort_keys=True) + (previous or "")
        return hashlib.sha256(payload.encode()).hexdigest()

def issue_receipt(tenant_id: str, actor: str, capability: str, policy_decision: str, model_version: str, input_payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> ActionReceipt:
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()
    return ActionReceipt(receipt_id=str(uuid.uuid4()), tenant_id=tenant_id, actor=actor, capability=capability, policy_decision=policy_decision, model_version=model_version, input_hash=input_hash, created_at=time.time(), metadata=metadata or {})
