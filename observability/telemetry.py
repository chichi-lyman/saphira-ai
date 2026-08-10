from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, CONTENT_TYPE_LATEST, generate_latest
from fastapi import APIRouter, Response

AGENT_EXECUTIONS_TOTAL = Counter(
    "saphira_agent_executions_total", "Total agent task executions", ["agent_did", "tenant_id", "status"]
)
AGENT_EXECUTION_LATENCY = Histogram(
    "saphira_agent_execution_latency_seconds", "Agent execution duration", ["agent_did", "action"]
)
AGENT_HEALTH_GAUGE = Gauge("saphira_agent_health_score", "Agent health score (0-100)", ["agent_did"])
ACTIVE_TENANT_COUNT = Gauge("saphira_active_tenants_total", "Active tenant count")

router = APIRouter(tags=["Observability"])


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
