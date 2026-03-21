from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.post import PeriodEnum, PostOut
from app.services.post_service import get_recent_posts, get_top_posts

router = APIRouter()


@router.get("/posts/top", response_model=list[PostOut])
def top_posts(
    channel_username: str | None = Query(default=None),
    period: PeriodEnum = Query(default=PeriodEnum.DAYS_7),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PostOut]:
    return get_top_posts(
        db=db,
        channel_username=channel_username,
        period=period.value,
        limit=limit,
    )


@router.get("/posts/recent", response_model=list[PostOut])
def recent_posts(
    channel_username: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PostOut]:
    return get_recent_posts(
        db=db,
        channel_username=channel_username,
        limit=limit,
    )
