from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import logging

from src.api.chat_router import router as chat_router
from src.api.memory_router import router as memory_router
from src.api.device_ws import router as device_router
from src.api.tiktok_router import router as tiktok_router
from src.api.platform_router import router as platform_router
from src.api.twilio_voice_router import router as twilio_voice_router
from src.api.saphira_dispatcher import router as saphira_dispatcher_router
from src.api.excellence_router import router as excellence_router
from src.api.autonomy_router import router as autonomy_router
from src.api.face_router import router as face_router
from src.commerce.stripe_checkout import router as checkout_router
from src.commerce.billing_router import router as billing_router
from core.control_plane import router as control_plane_router
from observability.telemetry import router as telemetry_router
from core.audit_middleware import AuditEventMiddleware
from src.config.settings import validate_environment
from src.connectors.saphira_mcp_client import router as mcp_router, mcp_manager

load_dotenv()
load_dotenv(".env.local", override=False)

logger = logging.getLogger("saphira")
settings = validate_environment(strict=False)

app = FastAPI(
    title="Saphira AI Enterprise",
    description="Conversational executive assistant with governed autonomous agents and enterprise control plane.",
    version="17.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list(),
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Stripe-Signature",
        "X-Saphira-Device",
        "X-Tenant-ID",
        "X-Agent-DID",
        "X-Saphira-Automation-Key",
        "X-Saphira-Memory-Key",
    ],
)
app.add_middleware(AuditEventMiddleware)

app.include_router(chat_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(device_router, prefix="/api")
app.include_router(tiktok_router, prefix="/api")
app.include_router(platform_router, prefix="/api")
app.include_router(twilio_voice_router, prefix="/api")
app.include_router(mcp_router, prefix="/api")
app.include_router(face_router, prefix="/api")  # /api/face/*
app.include_router(saphira_dispatcher_router)  # /v1/saphira/stream
app.include_router(excellence_router)  # /v1/router/execute
app.include_router(autonomy_router)  # /v1/autonomy/repair
app.include_router(checkout_router)
app.include_router(billing_router)
app.include_router(control_plane_router)
app.include_router(telemetry_router)

API_KEY_NAME = "X-Saphira-Sentinel-Token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_sentinel_token(api_key: str = Depends(api_key_header)):
    expected = __import__("os").getenv("SAPHIRA_SENTINEL_SECRET")
    if expected and api_key != expected:
        raise HTTPException(status_code=403, detail="Sentinel Authorization Failed")
    return api_key


@app.on_event("startup")
async def startup_mcp() -> None:
    """Bootstrap optional MCP servers from environment variables."""
    try:
        await mcp_manager.startup()
    except Exception as exc:
        logger.warning("MCP startup skipped or partial: %s", exc)
