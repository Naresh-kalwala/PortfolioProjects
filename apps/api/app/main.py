from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="AI Job Search & Resume Automation Platform",
    version="0.1.0",
    description="Discovers new job postings, tailors resumes with AI, and "
    "automates applications where a platform's terms of service allow it.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

if settings.storage_backend == "local":
    media_root = Path("/app/media") if Path("/app").exists() else Path("./media")
    media_root.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_root), name="media")


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}
