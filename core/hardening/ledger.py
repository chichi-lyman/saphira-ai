"""Append-only in-memory execution ledger for hardened action envelopes."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import time


@dataclass(frozen=True)
class LedgerEvent:
    execution_id: str
    tenant_id: str
    actor_id: str
    decision: str
    reason: str
    created_at: float


class ExecutionLedger:
    """Thread-safe append-only ledger used by the hardening boundary.

    Production persistence can be backed by Postgres; this class intentionally
    keeps the contract small so callers cannot mutate historical events.
    """

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._lock = Lock()

    def append(self, *, execution_id: str, tenant_id: str, actor_id: str,
               decision: str, reason: str) -> LedgerEvent:
        event = LedgerEvent(execution_id, tenant_id, actor_id, decision, reason, time())
        with self._lock:
            self._events.append(event)
        return event

    def events(self) -> tuple[LedgerEvent, ...]:
        with self._lock:
            return tuple(self._events)
