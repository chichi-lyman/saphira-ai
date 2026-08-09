from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from src.api.chat_router import router as chat_router
from src.api.device_ws import router as device_router

load_dotenv()

app = FastAPI(
    title="Saphira AI Production",
    description="Conversational executive assistant with autonomous background workers.",
    version="1.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("SAPHIRA_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Saphira-Device"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(device_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Saphira AI Production",
        "status": "running",
        "architecture": "executive-assistant",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
