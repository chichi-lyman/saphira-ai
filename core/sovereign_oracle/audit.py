"""Append-only SHA-256 hash-chain audit ledger (stdlib only).
Integrity/order proof is not proof of event truth. For durable custody, persist externally,
sign checkpoints, and control clock/key custody.
"""
from __future__ import annotations
import hashlib, json, os, threading, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

GENESIS = "0" * 64

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    timestamp_ns: int
    actor: str
    event_type: str
    payload: Mapping[str, Any]
    previous_hash: str
    record_hash: str
    def as_dict(self) -> dict[str, Any]:
        return {"sequence": self.sequence, "timestamp_ns": self.timestamp_ns, "actor": self.actor,
                "event_type": self.event_type, "payload": dict(self.payload),
                "previous_hash": self.previous_hash, "record_hash": self.record_hash}

class HashChainLedger:
    """Thread-safe append-only ledger optionally persisted as JSON Lines."""
    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._records: list[AuditRecord] = []
        self._lock = threading.RLock()
        if self.path and self.path.exists():
            self._load_and_verify()

    def append(self, actor: str, event_type: str, payload: Mapping[str, Any]) -> AuditRecord:
        if not actor.strip() or not event_type.strip():
            raise ValueError("actor and event_type must be non-empty")
        safe_payload = json.loads(canonical_json(dict(payload)))
        with self._lock:
            seq = len(self._records)
            prev = self._records[-1].record_hash if self._records else GENESIS
            core = {"sequence": seq, "timestamp_ns": time.time_ns(), "actor": actor,
                    "event_type": event_type, "payload": safe_payload, "previous_hash": prev}
            record = AuditRecord(**core, record_hash=sha256_hex(canonical_json(core)))
            if self.path:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as stream:
                    stream.write(canonical_json(record.as_dict()).decode("utf-8") + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
            self._records.append(record)
            return record

    def verify(self) -> bool:
        with self._lock:
            previous = GENESIS
            for seq, record in enumerate(self._records):
                core = {"sequence": record.sequence, "timestamp_ns": record.timestamp_ns,
                        "actor": record.actor, "event_type": record.event_type,
                        "payload": dict(record.payload), "previous_hash": record.previous_hash}
                if record.sequence != seq or record.previous_hash != previous:
                    return False
                if sha256_hex(canonical_json(core)) != record.record_hash:
                    return False
                previous = record.record_hash
            return True

    def records(self) -> tuple[AuditRecord, ...]:
        with self._lock:
            return tuple(self._records)

    def export_json(self) -> dict[str, Any]:
        return {"schema": "https://json-schema.org/draft/2020-12/schema",
                "ledger_type": "nova-umbrella-hash-chain-v1", "verified": self.verify(),
                "records": [r.as_dict() for r in self.records()]}

    def _load_and_verify(self) -> None:
        assert self.path is not None
        with self.path.open("r", encoding="utf-8") as stream:
            for line in stream:
                raw = json.loads(line)
                self._records.append(AuditRecord(**raw))
        if not self.verify():
            raise ValueError(f"Audit ledger integrity verification failed: {self.path}")

AUDIT_EXPORT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Nova Umbrella Audit Export", "type": "object",
    "required": ["schema", "ledger_type", "verified", "records"],
    "properties": {
        "schema": {"type": "string"},
        "ledger_type": {"const": "nova-umbrella-hash-chain-v1"},
        "verified": {"type": "boolean"},
        "records": {"type": "array", "items": {
            "type": "object",
            "required": ["sequence", "timestamp_ns", "actor", "event_type", "payload", "previous_hash", "record_hash"],
            "properties": {
                "sequence": {"type": "integer", "minimum": 0}, "timestamp_ns": {"type": "integer", "minimum": 0},
                "actor": {"type": "string", "minLength": 1}, "event_type": {"type": "string", "minLength": 1},
                "payload": {"type": "object"},
                "previous_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "record_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"}
            }, "additionalProperties": False
        }}
    }, "additionalProperties": False
}

def deterministic_memory_id(namespace: str, content: Mapping[str, Any]) -> str:
    """Stable content-addressed ID; does not claim semantic/vector retrieval."""
    if not namespace:
        raise ValueError("namespace must be non-empty")
    return sha256_hex(namespace.encode("utf-8") + b"\0" + canonical_json(dict(content)))
