from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.channel import ChannelListItem
from app.services.channel_service import ensure_configured_channels, list_channels

router = APIRouter()


@router.get("/channels", response_model=list[ChannelListItem])
def get_channels(db: Session = Depends(get_db)) -> list[ChannelListItem]:
    settings = get_settings()
    ensure_configured_channels(db, settings.telegram_channels)
    db.commit()
    return list_channels(db)
