"""Dependency-free telemetry primitives for model and agent operations."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from time import time
from typing import Any


@dataclass(frozen=True)
class OperationEvent:
    operation_id: str
    provider: str
    model_id: str
    task_id: str
    started_at: float
    latency_ms: float
    success: bool
    verified: bool | None = None
    estimated_cost_usd: float | None = None
    error_category: str | None = None


class OperationalTelemetry:
    """Thread-safe in-process metrics accumulator.

    Export snapshots to a durable store or metrics backend from the host service.
    Do not put prompts, outputs, credentials, or personal data in event labels.
    """

    def __init__(self) -> None:
        self._events: list[OperationEvent] = []
        self._lock = Lock()

    def record(
        self,
        *,
        operation_id: str,
        provider: str,
        model_id: str,
        task_id: str,
        started_at: float,
        latency_ms: float,
        success: bool,
        verified: bool | None = None,
        estimated_cost_usd: float | None = None,
        error_category: str | None = None,
    ) -> OperationEvent:
        if latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")
        if estimated_cost_usd is not None and estimated_cost_usd < 0:
            raise ValueError("estimated_cost_usd cannot be negative")
        event = OperationEvent(
            operation_id=operation_id,
            provider=provider,
            model_id=model_id,
            task_id=task_id,
            started_at=started_at,
            latency_ms=latency_ms,
            success=success,
            verified=verified,
            estimated_cost_usd=estimated_cost_usd,
            error_category=error_category,
        )
        with self._lock:
            self._events.append(event)
        return event

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            events = tuple(self._events)
        total = len(events)
        verified_events = [e for e in events if e.verified is not None]
        costs = [e.estimated_cost_usd for e in events if e.estimated_cost_usd is not None]
        by_model: dict[str, list[OperationEvent]] = defaultdict(list)
        for event in events:
            by_model[f"{event.provider}:{event.model_id}"].append(event)

        def summarize(items: tuple[OperationEvent, ...] | list[OperationEvent]) -> dict[str, Any]:
            count = len(items)
            latencies = sorted(e.latency_ms for e in items)
            successes = sum(1 for e in items if e.success)
            known_verification = [e for e in items if e.verified is not None]
            known_costs = [e.estimated_cost_usd for e in items if e.estimated_cost_usd is not None]
            return {
                "operations": count,
                "success_rate": successes / count if count else None,
                "latency_ms_avg": sum(latencies) / count if count else None,
                "latency_ms_p95": latencies[max(0, int(0.95 * len(latencies) + 0.999) - 1)] if latencies else None,
                "estimated_cost_usd_total": sum(known_costs) if known_costs else 0.0,
                "estimated_cost_usd_per_operation": (
                    sum(known_costs) / len(known_costs) if known_costs else None
                ),
                "verification_pass_rate": (
                    sum(1 for e in known_verification if e.verified) / len(known_verification)
                    if known_verification else None
                ),
            }

        result = summarize(events)
        result["verification_observations"] = len(verified_events)
        result["cost_observations"] = len(costs)
        result["by_model"] = {
            key: summarize(items) for key, items in sorted(by_model.items())
        }
        result["generated_at_epoch"] = time()
        return result
