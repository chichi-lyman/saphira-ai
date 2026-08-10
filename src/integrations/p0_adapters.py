"""P0 first-party adapters.

These adapters extract stable contracts from the existing satellite repositories
without copying their runtimes wholesale. They are intentionally dependency-
light so Saphira can test orchestration locally before external services are
configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


class AdapterError(RuntimeError):
    pass


class HealthProvider(Protocol):
    def health(self) -> dict[str, Any]: ...


@dataclass
class ASICoreAdapter:
    """Adapter for the cognitive planning contract in saphira-asi-core."""

    version: str = "Saphira-ASI-v3.0"
    persona: str = "Jarvis-Samantha-Hybrid"

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "asi-core", "version": self.version}

    def formulate_directive(self, query: str) -> dict[str, Any]:
        if not query or not query.strip():
            raise AdapterError("ASI query cannot be empty")
        plan = [
            "validate system security",
            "synthesize the optimal execution path",
            "dispatch the approved execution payload",
        ]
        return {
            "source": self.version,
            "persona": self.persona,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query.strip(),
            "strategic_plan": plan,
            "status": "DIRECTIVE_FORMULATED",
        }


@dataclass
class SalesSwarmAdapter:
    """Adapter for Saphira Sales Swarm's lead-generation workflow."""

    name: str = "saphira-sales-swarm"

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": self.name}

    def plan(self, industry: str, location: str, max_leads: int = 5) -> dict[str, Any]:
        if not industry.strip() or not location.strip():
            raise AdapterError("industry and location are required")
        if max_leads < 1 or max_leads > 1000:
            raise AdapterError("max_leads must be between 1 and 1000")
        return {
            "workflow": ["scout", "enrich", "strategize", "outreach"],
            "industry": industry.strip(),
            "location": location.strip(),
            "max_leads": max_leads,
            "approval_required": True,
            "status": "PENDING_APPROVAL",
        }


@dataclass
class SentinelAdapter:
    """Adapter around the Sentinel Suite's perimeter anomaly contract."""

    sentinel_id: str = "SENTINEL-ALPHA-01"

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "sentinel", "sentinel_id": self.sentinel_id}

    def scan(self, node_target: str, packet_metadata: dict[str, Any]) -> dict[str, Any]:
        if not node_target.strip():
            raise AdapterError("node_target is required")
        failed_auth = int(packet_metadata.get("failed_auth_attempts", 0))
        anomalous = failed_auth > 3
        return {
            "sentinel_id": self.sentinel_id,
            "target_node": node_target,
            "threat_status": "RED" if anomalous else "GREEN",
            "action": "QUARANTINE_AND_REVOKE" if anomalous else "PASS_THROUGH_VERIFIED",
            "anomalous": anomalous,
        }


@dataclass
class TwinVaultAdapter:
    """Safe in-memory adapter for tests; production secrets belong in a real vault."""

    _store: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self._store is None:
            self._store = {}

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "twin-vault", "mode": "test-memory"}

    def put_reference(self, key: str, secret_reference: str) -> None:
        if not key or not secret_reference:
            raise AdapterError("key and secret_reference are required")
        # Store a reference, never plaintext credentials.
        self._store[key] = secret_reference

    def get_reference(self, key: str) -> str | None:
        return self._store.get(key)


@dataclass
class SaphiraOSAdapter:
    """Interface adapter for the Saphira OS web/control-plane surface."""

    base_url: str = "http://localhost:3000"

    def health(self) -> dict[str, Any]:
        return {"status": "configured", "component": "saphira-os", "base_url": self.base_url}

    def route(self, surface: str) -> dict[str, str]:
        allowed = {"chat", "control_plane", "memory", "agents"}
        if surface not in allowed:
            raise AdapterError(f"Unknown Saphira OS surface: {surface}")
        return {"surface": surface, "url": f"{self.base_url.rstrip('/')}/{surface}"}
