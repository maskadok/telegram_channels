from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.models.channel_post import ChannelPost
from app.models.tracked_channel import TrackedChannel
from app.schemas.post import PostOut
from app.services.channel_service import normalize_channel_username
from app.utils.time import period_start


def _base_posts_query(channel_username: str | None = None) -> Select:
    stmt: Select = select(ChannelPost, TrackedChannel).join(
        TrackedChannel,
        TrackedChannel.id == ChannelPost.tracked_channel_id,
    )

    if channel_username:
        stmt = stmt.where(
            TrackedChannel.username == normalize_channel_username(channel_username),
        )

    return stmt


def _to_post_out(post: ChannelPost, channel: TrackedChannel) -> PostOut:
    return PostOut(
        id=post.id,
        channel_id=channel.id,
        channel_username=channel.username,
        channel_title=channel.title,
        telegram_message_id=post.telegram_message_id,
        message_date=post.message_date,
        text=post.text,
        views=post.views,
        forwards=post.forwards,
        replies_count=post.replies_count,
        reactions_total=post.reactions_total,
        channel_median_views=post.channel_median_views,
        alert_threshold_views=post.alert_threshold_views,
        popularity_score=post.popularity_score,
        is_alert_candidate=post.is_alert_candidate,
        alerted_at=post.alerted_at,
        collected_at=post.collected_at,
        telegram_url=f"https://t.me/{channel.username}/{post.telegram_message_id}",
    )


def get_top_posts(
    db: Session,
    channel_username: str | None,
    period: str,
    limit: int,
) -> list[PostOut]:
    #свежие посты
    stmt = _base_posts_query(channel_username=channel_username)
    period_from: datetime | None = period_start(period)
    if period_from is not None:
        stmt = stmt.where(ChannelPost.message_date >= period_from)

    stmt = stmt.order_by(
        desc(ChannelPost.message_date),
        desc(ChannelPost.id),
    ).limit(limit)

    return [_to_post_out(post, channel) for post, channel in db.execute(stmt).all()]


def get_recent_posts(
    db: Session,
    channel_username: str | None,
    limit: int,
) -> list[PostOut]:
    #выборка свежих постов
    stmt = _base_posts_query(channel_username=channel_username)
    stmt = stmt.order_by(desc(ChannelPost.message_date), desc(ChannelPost.id)).limit(limit)

    return [_to_post_out(post, channel) for post, channel in db.execute(stmt).all()]
