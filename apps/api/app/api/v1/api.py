from fastapi import APIRouter

from app.api.v1.routers import dashboard, jobs, notifications, profile, resumes

api_router = APIRouter()
api_router.include_router(jobs.router)
api_router.include_router(resumes.router)
api_router.include_router(profile.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
