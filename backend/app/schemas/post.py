from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PeriodEnum(str, Enum):
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    ALL = "all"


class PostOut(BaseModel):
    id: int
    channel_id: int
    channel_username: str
    channel_title: str
    telegram_message_id: int
    message_date: datetime
    text: str | None
    views: int
    forwards: int
    replies_count: int
    reactions_total: int
    channel_median_views: float
    alert_threshold_views: float
    popularity_score: float
    is_alert_candidate: bool
    alerted_at: datetime | None
    collected_at: datetime
    telegram_url: str
