"""SOC2-oriented evidence pack export."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class EvidencePack:
    tenant_id: str
    generated_at: float
    window_start: Optional[float]
    window_end: Optional[float]
    records: List[Dict[str, Any]] = field(default_factory=list)
    model_versions: List[str] = field(default_factory=list)
    policy_version: str = "1.0"
    def to_json(self) -> str:
        return json.dumps({"tenant_id": self.tenant_id, "generated_at": self.generated_at, "window_start": self.window_start, "window_end": self.window_end, "policy_version": self.policy_version, "model_versions": self.model_versions, "record_count": len(self.records), "records": self.records}, indent=2, sort_keys=True)

class EvidenceExporter:
    def export(self, tenant_id: str, records: List[Dict[str, Any]], window_start: Optional[float] = None, window_end: Optional[float] = None, model_versions: Optional[List[str]] = None) -> EvidencePack:
        return EvidencePack(tenant_id=tenant_id, generated_at=time.time(), window_start=window_start, window_end=window_end, records=list(records), model_versions=model_versions or [])

evidence_exporter = EvidenceExporter()
