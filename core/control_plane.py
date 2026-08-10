from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from governance.health_monitor import AgentHealthMonitor, AgentHealthReport
from storage.database import require_database

router = APIRouter(prefix="/v1/control-plane", tags=["Enterprise Control Plane"])


class AgentDeployRequest(BaseModel):
    agent_did: str
    target_tenant_id: str
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class SystemOverviewResponse(BaseModel):
    active_tenants: int
    installed_agents: int
    health_status: str
    total_ledger_volume_usd: float


@router.get("/overview", response_model=SystemOverviewResponse)
async def get_system_overview(x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    SessionFactory = require_database()
    async with SessionFactory() as session:
        await session.execute(text("SELECT set_config('app.current_tenant', :tenant, true)"), {"tenant": x_tenant_id})
        installs = await session.execute(text("SELECT COUNT(*) FROM agent_installations WHERE status='ACTIVE'"))
        volume = await session.execute(text("SELECT COALESCE(SUM(gross_amount_usd),0) FROM agent_revenue_transactions"))
    return SystemOverviewResponse(
        active_tenants=1,
        installed_agents=int(installs.scalar() or 0),
        health_status="OPERATIONAL",
        total_ledger_volume_usd=float(volume.scalar() or 0),
    )


@router.post("/marketplace/install", status_code=status.HTTP_201_CREATED)
async def install_marketplace_agent(payload: AgentDeployRequest, x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    if payload.target_tenant_id != x_tenant_id:
        raise HTTPException(status_code=403, detail="Target tenant does not match authenticated tenant context")
    SessionFactory = require_database()
    async with SessionFactory() as session:
        async with session.begin():
            await session.execute(text("SELECT set_config('app.current_tenant', :tenant, true)"), {"tenant": x_tenant_id})
            result = await session.execute(text("SELECT version FROM agent_marketplace WHERE agent_did=:did AND is_verified=true"), {"did": payload.agent_did})
            item = result.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="Verified marketplace agent not found")
            await session.execute(text("""
                INSERT INTO agent_installations (tenant_id, agent_did, installed_version, status, config_overrides)
                VALUES (:tenant, :did, :version, 'ACTIVE', CAST(:config AS jsonb))
                ON CONFLICT (tenant_id, agent_did) DO UPDATE SET status='ACTIVE', installed_version=:version,
                    config_overrides=CAST(:config AS jsonb), updated_at=CURRENT_TIMESTAMP
            """), {"tenant": x_tenant_id, "did": payload.agent_did, "version": item[0], "config": __import__('json').dumps(payload.config_overrides)})
    return {"status": "SUCCESS", "agent_did": payload.agent_did, "tenant_id": x_tenant_id}


@router.get("/agents/{agent_did}/health", response_model=AgentHealthReport)
async def get_agent_health_telemetry(agent_did: str):
    return AgentHealthMonitor.calculate_health_score(agent_did, 0.98, 0.92, 1.45, 1.02)
