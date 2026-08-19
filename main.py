from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

from src.api.chat_router import router as chat_router
from src.api.device_ws import router as device_router
from src.api.tiktok_router import router as tiktok_router
from src.api.platform_router import router as platform_router
from src.commerce.stripe_checkout import router as checkout_router
from core.control_plane import router as control_plane_router
from observability.telemetry import router as telemetry_router
from core.audit_middleware import AuditEventMiddleware
from src.config.settings import get_settings, validate_environment

load_dotenv()
load_dotenv(".env.local", override=False)

logger = logging.getLogger("saphira")
settings = validate_environment(strict=False)

app = FastAPI(
    title="Saphira AI Enterprise",
    description="Conversational executive assistant with governed autonomous agents and enterprise control plane.",
    version="17.0.0",
)

allowed_origins = settings.allowed_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\\.vercel\\.app$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Saphira-Device", "X-Tenant-ID", "X-Agent-DID", "X-Saphira-Automation-Key"],
)
app.add_middleware(AuditEventMiddleware)

app.include_router(chat_router, prefix="/api")
app.include_router(device_router, prefix="/api")
app.include_router(tiktok_router, prefix="/api")
app.include_router(platform_router, prefix="/api")
app.include_router(checkout_router)
app.include_router(control_plane_router)
app.include_router(telemetry_router)


@app.get("/")
async def root():
    return {
        "name": "Saphira AI",
        "status": "running",
        "version": "17.0.0",
        "role": "conversational-ai-assistant",
        "architecture": "autonomous-agent-operating-platform",
        "platform_layer": "enabled",
        "environment": settings.environment,
    }


@app.get("/health")
async def health():
    report = settings.validation_report()
    return {"status": "healthy", "service": "saphira-ai", "version": "17.0.0", "config": report}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
