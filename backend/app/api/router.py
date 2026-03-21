from fastapi import APIRouter

from app.api.channels import router as channels_router
from app.api.health import router as health_router
from app.api.posts import router as posts_router
from app.api.sync import router as sync_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(channels_router, prefix="/api", tags=["channels"])
api_router.include_router(posts_router, prefix="/api", tags=["posts"])
api_router.include_router(sync_router, prefix="/api", tags=["sync"])
