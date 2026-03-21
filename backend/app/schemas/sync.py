from dataclasses import asdict
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.services.telegram_sync import SyncSummary


class SyncRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=500)
    channel_usernames: list[str] | None = None

    @field_validator("channel_usernames", mode="before")
    @classmethod
    def normalize_channel_usernames(cls, value: list[str] | str | None) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            values = value.split(",")
        else:
            values = value
        return [item.strip() for item in values if item and item.strip()]


class SyncChannelError(BaseModel):
    username: str
    error: str


class SyncResponse(BaseModel):
    started_at: datetime
    finished_at: datetime
    channels_total: int
    channels_processed: int
    posts_created: int
    posts_updated: int
    errors: list[SyncChannelError]

    @classmethod
    def from_summary(cls, summary: SyncSummary) -> "SyncResponse":
        return cls(**asdict(summary))
