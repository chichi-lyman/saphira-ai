"""Append-only, hash-chained audit subsystem for commercial actions.

Records what actually happened (including failed/denied attempts), not merely
what was intended. Hash chaining makes unauthorized modification detectable.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_record(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str
    execution_id: str
    timestamp: str
    actor: str
    action: str
    target_type: str
    target_id: str
    policy_decision: str
    reason: str
    previous_state: str
    resulting_state: str
    event_id: str
    metadata: dict[str, Any]
    previous_hash: str
    record_hash: str
    executed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuditStore:
    """In-memory append-only audit store with hash chaining.

    Production deployments should back this with an append-only table and
    infrastructure permissions that prevent UPDATE/DELETE of historical rows.
    """

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    @property
    def records(self) -> list[AuditRecord]:
        return list(self._records)

    def last_hash(self) -> str:
        if not self._records:
            return "0" * 64
        return self._records[-1].record_hash

    def append(
        self,
        *,
        actor: str,
        action: str,
        target_type: str,
        target_id: str,
        policy_decision: str,
        reason: str,
        previous_state: str = "",
        resulting_state: str = "",
        event_id: str = "",
        metadata: dict[str, Any] | None = None,
        execution_id: str | None = None,
        executed: bool = False,
    ) -> AuditRecord:
        previous_hash = self.last_hash()
        audit_id = str(uuid.uuid4())
        execution_id = execution_id or str(uuid.uuid4())
        timestamp = _utc_now()
        meta = dict(metadata or {})

        hash_payload = {
            "audit_id": audit_id,
            "execution_id": execution_id,
            "timestamp": timestamp,
            "actor": actor,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "policy_decision": policy_decision,
            "reason": reason,
            "previous_state": previous_state,
            "resulting_state": resulting_state,
            "event_id": event_id,
            "metadata": meta,
            "executed": executed,
            "previous_hash": previous_hash,
        }
        record_hash = _hash_record(hash_payload)

        record = AuditRecord(
            audit_id=audit_id,
            execution_id=execution_id,
            timestamp=timestamp,
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=target_id,
            policy_decision=policy_decision,
            reason=reason,
            previous_state=previous_state,
            resulting_state=resulting_state,
            event_id=event_id,
            metadata=meta,
            previous_hash=previous_hash,
            record_hash=record_hash,
            executed=executed,
        )
        self._records.append(record)
        return record

    def verify_chain(self) -> tuple[bool, str]:
        """Return (ok, detail). Detects broken chain or content tampering."""
        expected_prev = "0" * 64
        for i, rec in enumerate(self._records):
            if rec.previous_hash != expected_prev:
                return False, f"Broken chain at index {i}: expected previous_hash {expected_prev}, got {rec.previous_hash}"
            hash_payload = {
                "audit_id": rec.audit_id,
                "execution_id": rec.execution_id,
                "timestamp": rec.timestamp,
                "actor": rec.actor,
                "action": rec.action,
                "target_type": rec.target_type,
                "target_id": rec.target_id,
                "policy_decision": rec.policy_decision,
                "reason": rec.reason,
                "previous_state": rec.previous_state,
                "resulting_state": rec.resulting_state,
                "event_id": rec.event_id,
                "metadata": rec.metadata,
                "executed": rec.executed,
                "previous_hash": rec.previous_hash,
            }
            computed = _hash_record(hash_payload)
            if computed != rec.record_hash:
                return False, f"Hash mismatch at index {i}: record may have been tampered"
            expected_prev = rec.record_hash
        return True, f"Chain intact ({len(self._records)} records)"

    def filter(
        self,
        *,
        action: str | None = None,
        target_id: str | None = None,
        event_id: str | None = None,
    ) -> list[AuditRecord]:
        result: list[AuditRecord] = []
        for rec in self._records:
            if action is not None and rec.action != action:
                continue
            if target_id is not None and rec.target_id != target_id:
                continue
            if event_id is not None and rec.event_id != event_id:
                continue
            result.append(rec)
        return result
