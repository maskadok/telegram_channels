from datetime import datetime

from pydantic import BaseModel


class ChannelListItem(BaseModel):
    id: int
    username: str
    title: str
    is_active: bool
    posts_count: int
    latest_post_date: datetime | None
    updated_at: datetime
