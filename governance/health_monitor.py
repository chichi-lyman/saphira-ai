from __future__ import annotations

from pydantic import BaseModel


class AgentHealthReport(BaseModel):
    agent_did: str
    health_score: float
    status: str
    metrics_breakdown: dict[str, float]


class AgentHealthMonitor:
    @staticmethod
    def calculate_health_score(
        agent_did: str,
        success_rate: float,
        trust_score: float,
        p95_latency_sec: float,
        cost_drift_ratio: float,
    ) -> AgentHealthReport:
        success_rate = max(0.0, min(1.0, success_rate))
        trust_score = max(0.0, min(1.0, trust_score))
        latency_score = max(0.0, min(1.0, (10.0 - max(0.0, p95_latency_sec)) / 8.0))
        cost_penalty = max(0.0, min(1.0, cost_drift_ratio - 1.0))
        raw = success_rate * 40 + trust_score * 30 + latency_score * 20 - cost_penalty * 10
        score = round(max(0.0, min(100.0, raw)), 2)
        status = "HEALTHY" if score >= 80 else "DEGRADED" if score >= 50 else "UNHEALTHY"
        return AgentHealthReport(
            agent_did=agent_did,
            health_score=score,
            status=status,
            metrics_breakdown={
                "success_rate_component": round(success_rate * 40, 2),
                "trust_score_component": round(trust_score * 30, 2),
                "latency_component": round(latency_score * 20, 2),
                "cost_penalty_deduction": round(cost_penalty * 10, 2),
            },
        )
