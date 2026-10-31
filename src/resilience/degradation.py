# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella

"""
Graceful degradation levels for Saphira when providers or tools are impaired.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Optional
import logging

logger = logging.getLogger("Saphira.Degradation")


class DegradationLevel(IntEnum):
    FULL = 0          # all providers/tools healthy
    REDUCED = 1       # primary down, fallbacks active
    MINIMAL = 2       # only cheapest / most reliable path
    STANDBY = 3       # no external LLM; safe local reply only


class GracefulDegradation:
    """Tracks overall system degradation and recommends response policy."""

    def __init__(self):
        self._level = DegradationLevel.FULL
        self._reasons: list[str] = []

    @property
    def level(self) -> DegradationLevel:
        return self._level

    def update_from_provider_health(self, health: dict[str, Any]) -> DegradationLevel:
        """
        health shape expected from ProviderRegistry.health()['providers']:
        { name: {enabled, configured, circuit: {...}} }
        """
        providers = health.get("providers") or health
        enabled_ok = 0
        total_enabled = 0
        open_circuits = 0

        for name, snap in providers.items():
            if not isinstance(snap, dict):
                continue
            if snap.get("enabled"):
                total_enabled += 1
                circuit = snap.get("circuit") or {}
                if circuit.get("state") == "open":
                    open_circuits += 1
                else:
                    enabled_ok += 1

        self._reasons = []
        if total_enabled == 0:
            self._level = DegradationLevel.STANDBY
            self._reasons.append("no_enabled_providers")
        elif enabled_ok == 0:
            self._level = DegradationLevel.STANDBY
            self._reasons.append("all_circuits_open")
        elif open_circuits > 0 and enabled_ok == 1:
            self._level = DegradationLevel.MINIMAL
            self._reasons.append("single_provider_left")
        elif open_circuits > 0:
            self._level = DegradationLevel.REDUCED
            self._reasons.append(f"{open_circuits}_circuits_open")
        else:
            self._level = DegradationLevel.FULL

        if self._level != DegradationLevel.FULL:
            logger.info("degradation level=%s reasons=%s", self._level.name, self._reasons)
        return self._level

    def standby_message(self, original_error: Optional[str] = None) -> str:
        base = (
            "[Saphira Standby] I'm temporarily running on reduced capacity. "
            "Your request was received and will be processed as soon as providers recover."
        )
        if original_error:
            return f"{base} (detail: {original_error[:120]})"
        return base

    def snapshot(self) -> dict[str, Any]:
        return {
            "level": self._level.name,
            "level_int": int(self._level),
            "reasons": list(self._reasons),
        }
