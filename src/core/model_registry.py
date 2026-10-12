"""Provider-neutral model registry and deterministic routing contracts.

This module does not call external providers. Provider adapters register their
capabilities and supply an invocation callable at application startup.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model_id: str
    capabilities: frozenset[str] = frozenset({"chat"})
    modalities: frozenset[Modality] = frozenset({Modality.TEXT})
    enabled: bool = False
    max_input_tokens: int | None = None
    cost_per_1k_input_tokens: float | None = None
    cost_per_1k_output_tokens: float | None = None
    max_latency_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.provider}:{self.model_id}"


@dataclass(frozen=True)
class RoutingRequest:
    capability: str = "chat"
    required_modalities: frozenset[Modality] = frozenset({Modality.TEXT})
    max_cost_per_1k_input_tokens: float | None = None
    max_latency_ms: int | None = None
    preferred_providers: tuple[str, ...] = ()
    allow_disabled: bool = False


@dataclass(frozen=True)
class RoutingDecision:
    selected: ModelSpec
    candidates: tuple[str, ...]
    reason: str


class NoEligibleModelError(RuntimeError):
    """Raised when no registered model satisfies a routing request."""


class ModelRegistry:
    """In-memory registry; production persistence/configuration belongs to the host app."""

    def __init__(self) -> None:
        self._models: dict[str, ModelSpec] = {}
        self._invokers: dict[str, Callable[..., Any]] = {}

    def register(
        self, spec: ModelSpec, invoker: Callable[..., Any] | None = None
    ) -> None:
        if not spec.provider.strip() or not spec.model_id.strip():
            raise ValueError("provider and model_id must be non-empty")
        if spec.cost_per_1k_input_tokens is not None and spec.cost_per_1k_input_tokens < 0:
            raise ValueError("input token cost cannot be negative")
        if spec.cost_per_1k_output_tokens is not None and spec.cost_per_1k_output_tokens < 0:
            raise ValueError("output token cost cannot be negative")
        if spec.max_latency_ms is not None and spec.max_latency_ms <= 0:
            raise ValueError("max_latency_ms must be positive")
        self._models[spec.key] = spec
        if invoker is not None:
            self._invokers[spec.key] = invoker
        else:
            self._invokers.pop(spec.key, None)

    def unregister(self, key: str) -> None:
        self._models.pop(key, None)
        self._invokers.pop(key, None)

    def get(self, key: str) -> ModelSpec | None:
        return self._models.get(key)

    def list_models(self, *, include_disabled: bool = True) -> tuple[ModelSpec, ...]:
        models = self._models.values()
        if not include_disabled:
            models = (m for m in models if m.enabled)
        return tuple(sorted(models, key=lambda m: m.key))

    def route(self, request: RoutingRequest) -> RoutingDecision:
        eligible: list[ModelSpec] = []
        for model in self._models.values():
            if not request.allow_disabled and not model.enabled:
                continue
            if request.capability not in model.capabilities:
                continue
            if not request.required_modalities.issubset(model.modalities):
                continue
            if request.max_cost_per_1k_input_tokens is not None:
                cost = model.cost_per_1k_input_tokens
                if cost is None or cost > request.max_cost_per_1k_input_tokens:
                    continue
            latency = request.max_latency_ms
            if latency is not None and (
                model.max_latency_ms is None or model.max_latency_ms > latency
            ):
                continue
            eligible.append(model)

        if not eligible:
            raise NoEligibleModelError(
                "No enabled registered model satisfies capability, modality, cost, and latency constraints"
            )

        preference = {name: i for i, name in enumerate(request.preferred_providers)}
        eligible.sort(
            key=lambda m: (
                preference.get(m.provider, len(preference)),
                m.cost_per_1k_input_tokens
                if m.cost_per_1k_input_tokens is not None
                else float("inf"),
                m.max_latency_ms if m.max_latency_ms is not None else float("inf"),
                m.key,
            )
        )
        selected = eligible[0]
        return RoutingDecision(
            selected=selected,
            candidates=tuple(m.key for m in eligible),
            reason="eligible model ranked by provider preference, declared cost, latency, then stable key",
        )

    def invoke(self, decision: RoutingDecision, **kwargs: Any) -> Any:
        invoker = self._invokers.get(decision.selected.key)
        if invoker is None:
            raise RuntimeError(f"No invoker registered for {decision.selected.key}")
        return invoker(**kwargs)
