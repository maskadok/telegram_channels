from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.channel_post import ChannelPost
from app.models.tracked_channel import TrackedChannel
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request, db: Session = Depends(get_db)) -> HealthResponse:
    tracked_channels = db.scalar(select(func.count(TrackedChannel.id))) or 0
    stored_posts = db.scalar(select(func.count(ChannelPost.id))) or 0
    scheduler = getattr(request.app.state, "scheduler", None)
    settings = request.app.state.settings

    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        database="ok",
        tracked_channels=tracked_channels,
        stored_posts=stored_posts,
        scheduler_running=bool(scheduler and scheduler.is_running),
    )
