from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("SaphiraMain")

# Get deployment configuration from environment
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
VERCEL_URL = os.getenv("VERCEL_URL", "localhost:3000")
NODE_ENV = os.getenv("NODE_ENV", "development")

# Explicit CORS origins for production/staging/dev
if NODE_ENV == "production":
    ALLOWED_ORIGINS = [
        f"https://{VERCEL_URL}",           # Vercel frontend
        f"https://{RAILWAY_PUBLIC_DOMAIN}",  # Railway backend (self-reference)
        "https://saphira-delta.vercel.app",  # Explicit production URL
    ]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:3000",   # Local web dev
        "http://localhost:8000",   # Local API dev
        "http://localhost:8080",   # Flutter dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        f"https://{VERCEL_URL}",
        f"https://{RAILWAY_PUBLIC_DOMAIN}",
    ]

logger.info(f"Saphira starting in {NODE_ENV} mode")
logger.info(f"Allowed CORS origins: {ALLOWED_ORIGINS}")

# Create FastAPI app
app = FastAPI(
    title="Saphira AI",
    description="Proactive Personal Assistant with Multi-Agent Orchestration",
    version="1.0.0",
    docs_url="/docs" if NODE_ENV != "production" else None,
    redoc_url="/redoc" if NODE_ENV != "production" else None,
)

# Configure CORS Middleware with explicit origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Saphira AI",
        "status": "running",
        "environment": NODE_ENV,
        "version": "1.0.0",
        "creator": "Chelsea Megan Woods",
        "studio": "Woods AI Studio / Lyman Legacies"
    }

# Health check endpoint (used by Railway, Vercel, and load balancers)
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": NODE_ENV,
        "timestamp": None  # Will be filled by datetime in production
    }

# Configuration endpoint (safe for frontend)
@app.get("/config")
async def get_config():
    """Return safe configuration for frontend."""
    return {
        "api_url": RAILWAY_PUBLIC_DOMAIN,
        "environment": NODE_ENV,
        "cors_enabled": True,
        "features": {
            "voice_enabled": bool(os.getenv("ELEVENLABS_API_KEY")),
            "home_assistant": bool(os.getenv("HOME_ASSISTANT_URL")),
            "biometrics": bool(os.getenv("WEARABLE_API_KEY")),
        }
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = NODE_ENV == "development"
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
