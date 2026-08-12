from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from src.api.chat_router import router as chat_router
from src.api.device_ws import router as device_router
from src.api.tiktok_router import router as tiktok_router
from src.api.platform_router import router as platform_router
from core.control_plane import router as control_plane_router
from observability.telemetry import router as telemetry_router
from core.audit_middleware import AuditEventMiddleware

load_dotenv()

app = FastAPI(
    title="Saphira AI Enterprise",
    description="Conversational executive assistant with governed autonomous agents and enterprise control plane.",
    version="17.0.0",
)

allowed_origins = [
    o.strip()
    for o in os.getenv("SAPHIRA_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Saphira-Device", "X-Tenant-ID", "X-Agent-DID", "X-Saphira-Automation-Key"],
)
app.add_middleware(AuditEventMiddleware)

app.include_router(chat_router, prefix="/api")
app.include_router(device_router, prefix="/api")
app.include_router(tiktok_router, prefix="/api")
app.include_router(platform_router, prefix="/api")
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
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "saphira-ai", "version": "17.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
