from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.time import utcnow


class ChannelPost(Base):
    __tablename__ = "channel_posts"
    __table_args__ = (
        UniqueConstraint(
            "tracked_channel_id",
            "telegram_message_id",
            name="uq_channel_posts_channel_message",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tracked_channel_id: Mapped[int] = mapped_column(
        ForeignKey("tracked_channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    telegram_message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forwards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    replies_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reactions_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    channel_median_views: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    alert_threshold_views: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    popularity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    is_alert_candidate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    alerted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    tracked_channel = relationship("TrackedChannel", back_populates="posts")
