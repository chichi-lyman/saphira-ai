"""P0 first-party adapters."""
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
    version: str = "Saphira-ASI-v3.0"
    persona: str = "Jarvis-Samantha-Hybrid"

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "asi-core", "version": self.version}

    def formulate_directive(self, query: str) -> dict[str, Any]:
        if not query or not query.strip():
            raise AdapterError("ASI query cannot be empty")
        return {
            "source": self.version, "persona": self.persona,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query.strip(),
            "strategic_plan": ["validate system security", "synthesize the optimal execution path", "dispatch the approved execution payload"],
            "status": "DIRECTIVE_FORMULATED",
        }


@dataclass
class SalesSwarmAdapter:
    """Sales discovery + profiling adapter with mandatory human approval."""
    name: str = "saphira-sales-swarm"

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": self.name}

    def plan(self, industry: str, location: str, max_leads: int = 5) -> dict[str, Any]:
        if not industry.strip() or not location.strip():
            raise AdapterError("industry and location are required")
        if max_leads < 1 or max_leads > 1000:
            raise AdapterError("max_leads must be between 1 and 1000")
        return {"workflow": ["scout", "profile", "qualify", "draft", "approval"], "industry": industry.strip(), "location": location.strip(), "max_leads": max_leads, "approval_required": True, "status": "PENDING_APPROVAL"}

    def discover_fixture_leads(self, html_text: str, *, source_url: str, source_name: str, industry: str, city: str = "", state: str = "", max_leads: int = 50) -> list[dict[str, Any]]:
        from src.tools.free_scraper import parse_fixture_html
        if max_leads < 1 or max_leads > 1000:
            raise AdapterError("max_leads must be between 1 and 1000")
        leads = parse_fixture_html(html_text, source_url=source_url, source_name=source_name, industry=industry, city=city, state=state)
        return [self._lead_dict(lead) for lead in leads[:max_leads]]

    def profile_and_queue(self, leads: list[dict[str, Any]], output: str = "storage/tampa_roofing_approval_queue.csv") -> dict[str, Any]:
        """Profile normalized leads and write a review-only CSV queue."""
        from src.tools.free_scraper import Lead
        from src.tools.tampa_roofing_pipeline import profile_lead, write_approval_queue, write_summary
        normalized = [Lead(**{k: row.get(k, "") for k in Lead.__dataclass_fields__}) for row in leads]
        profiles = [profile_lead(lead) for lead in normalized]
        queue = write_approval_queue(profiles, output)
        summary = write_summary(profiles, output.replace(".csv", "_summary.md"))
        return {"status": "PENDING_APPROVAL", "count": len(profiles), "queue": str(queue), "summary": str(summary), "external_send_enabled": False}

    @staticmethod
    def _lead_dict(lead: Any) -> dict[str, Any]:
        return {"business_name": lead.business_name, "website": lead.website, "business_phone": lead.business_phone, "city": lead.city, "state": lead.state, "industry": lead.industry, "source_url": lead.source_url, "source_name": lead.source_name, "discovered_at": lead.discovered_at}


@dataclass
class SentinelAdapter:
    sentinel_id: str = "SENTINEL-ALPHA-01"
    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "sentinel", "sentinel_id": self.sentinel_id}
    def scan(self, node_target: str, packet_metadata: dict[str, Any]) -> dict[str, Any]:
        if not node_target.strip(): raise AdapterError("node_target is required")
        anomalous = int(packet_metadata.get("failed_auth_attempts", 0)) > 3
        return {"sentinel_id": self.sentinel_id, "target_node": node_target, "threat_status": "RED" if anomalous else "GREEN", "action": "QUARANTINE_AND_REVOKE" if anomalous else "PASS_THROUGH_VERIFIED", "anomalous": anomalous}


@dataclass
class TwinVaultAdapter:
    _store: dict[str, str] | None = None
    def __post_init__(self) -> None:
        if self._store is None: self._store = {}
    def health(self) -> dict[str, Any]: return {"status": "ok", "component": "twin-vault", "mode": "test-memory"}
    def put_reference(self, key: str, secret_reference: str) -> None:
        if not key or not secret_reference: raise AdapterError("key and secret_reference are required")
        self._store[key] = secret_reference
    def get_reference(self, key: str) -> str | None: return self._store.get(key)


@dataclass
class SaphiraOSAdapter:
    base_url: str = "http://localhost:3000"
    def health(self) -> dict[str, Any]: return {"status": "configured", "component": "saphira-os", "base_url": self.base_url}
    def route(self, surface: str) -> dict[str, str]:
        if surface not in {"chat", "control_plane", "memory", "agents"}: raise AdapterError(f"Unknown Saphira OS surface: {surface}")
        return {"surface": surface, "url": f"{self.base_url.rstrip('/')}/{surface}"}
