from __future__ import annotations

import json

import pytest

from core.sovereign_oracle.audit import (
    GENESIS,
    HashChainLedger,
    canonical_json,
    deterministic_memory_id,
)


def test_canonical_json_is_key_order_independent() -> None:
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})


def test_memory_id_is_deterministic_and_namespaced() -> None:
    value = {"prompt": "hello", "version": 1}
    assert deterministic_memory_id("tenant-a", value) == deterministic_memory_id("tenant-a", value)
    assert deterministic_memory_id("tenant-a", value) != deterministic_memory_id("tenant-b", value)


def test_ledger_chains_records_and_exports_verified_state() -> None:
    ledger = HashChainLedger()
    first = ledger.append("agent-a", "task.started", {"task_id": "t-1"})
    second = ledger.append("agent-a", "task.completed", {"task_id": "t-1"})

    assert first.sequence == 0
    assert first.previous_hash == GENESIS
    assert second.sequence == 1
    assert second.previous_hash == first.record_hash
    assert ledger.verify()
    exported = ledger.export_json()
    assert exported["verified"] is True
    assert len(exported["records"]) == 2


def test_persisted_ledger_reloads_and_detects_tampering(tmp_path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = HashChainLedger(path)
    ledger.append("agent-a", "task.started", {"task_id": "t-1"})
    ledger.append("agent-a", "task.completed", {"task_id": "t-1"})

    restored = HashChainLedger(path)
    assert restored.verify()
    assert len(restored.records()) == 2

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["payload"]["task_id"] = "tampered"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity verification failed"):
        HashChainLedger(path)


@pytest.mark.parametrize(
    ("actor", "event_type"),
    [("", "event"), ("agent", ""), ("  ", "event"), ("agent", "  ")],
)
def test_ledger_rejects_empty_actor_or_event(actor: str, event_type: str) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        HashChainLedger().append(actor, event_type, {})
