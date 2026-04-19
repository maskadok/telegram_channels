from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.models.channel_post import ChannelPost
from app.models.tracked_channel import TrackedChannel
from app.schemas.channel import ChannelListItem


def normalize_channel_username(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.removeprefix("https://t.me/")
    normalized = normalized.removeprefix("http://t.me/")
    normalized = normalized.removeprefix("t.me/")
    normalized = normalized.removeprefix("@")
    return normalized.strip("/")


#каналы из настроек
def ensure_configured_channels(db: Session, channel_usernames: list[str]) -> int:
    created = 0
    seen: set[str] = set()

    for raw_username in channel_usernames:
        username = normalize_channel_username(raw_username)
        if not username or username in seen:
            continue

        seen.add(username)
        channel = db.scalar(select(TrackedChannel).where(TrackedChannel.username == username))
        if channel is None:
            db.add(
                TrackedChannel(
                    username=username,
                    title=username,
                    is_active=True,
                ),
            )
            created += 1
        else:
            channel.is_active = True

    db.query(TrackedChannel).filter(TrackedChannel.username.not_in(seen)).update(
        {TrackedChannel.is_active: False},
        synchronize_session=False,
    )

    return created


def list_channels(db: Session) -> list[ChannelListItem]:
    #сводка по каналам
    stats_subquery = (
        select(
            ChannelPost.tracked_channel_id.label("channel_id"),
            func.count(ChannelPost.id).label("posts_count"),
            func.max(ChannelPost.message_date).label("latest_post_date"),
        )
        .group_by(ChannelPost.tracked_channel_id)
        .subquery()
    )

    stmt: Select = (
        select(
            TrackedChannel,
            func.coalesce(stats_subquery.c.posts_count, 0),
            stats_subquery.c.latest_post_date,
        )
        .outerjoin(stats_subquery, stats_subquery.c.channel_id == TrackedChannel.id)
        .where(TrackedChannel.is_active.is_(True))
        .order_by(TrackedChannel.username.asc())
    )

    items: list[ChannelListItem] = []
    for channel, posts_count, latest_post_date in db.execute(stmt).all():
        items.append(
            ChannelListItem(
                id=channel.id,
                username=channel.username,
                title=channel.title,
                is_active=channel.is_active,
                posts_count=int(posts_count or 0),
                latest_post_date=latest_post_date,
                updated_at=channel.updated_at,
            ),
        )

    return items
