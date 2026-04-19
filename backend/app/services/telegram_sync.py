from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from telethon.tl.custom.message import Message

from app.core.config import Settings
from app.models.channel_post import ChannelPost
from app.models.tracked_channel import TrackedChannel
from app.services.channel_service import ensure_configured_channels, normalize_channel_username
from app.services.telegram_client import TelegramClientService
from app.utils.metrics import (
    ANALYTICS_LOOKBACK_DAYS,
    calculate_alert_threshold,
    calculate_channel_median_views,
    calculate_popularity_score,
    should_alert_post,
)
from app.utils.time import utcnow

logger = logging.getLogger(__name__)


class SyncInProgressError(RuntimeError):
    pass


@dataclass
class SyncChannelIssue:
    username: str
    error: str


@dataclass
class SyncSummary:
    started_at: datetime
    finished_at: datetime
    channels_total: int
    channels_processed: int
    posts_created: int
    posts_updated: int
    errors: list[SyncChannelIssue] = field(default_factory=list)


@dataclass
class ParsedTelegramPost:
    telegram_message_id: int
    message_date: datetime
    text: str | None
    views: int
    forwards: int
    replies_count: int
    reactions_total: int
    collected_at: datetime
    raw_json: dict[str, Any] | None
    channel_median_views: float = 0.0
    alert_threshold_views: float = 0.0
    popularity_score: float = 0.0
    is_alert_candidate: bool = False
    alerted_at: datetime | None = None


#синк каналов
class TelegramSyncService:
    def __init__(self, settings: Settings, session_factory: sessionmaker[Session]) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.client_service = TelegramClientService(settings)
        self._lock = asyncio.Lock()

    async def sync_channels(
        self,
        channel_usernames: list[str] | None = None,
        limit: int | None = None,
    ) -> SyncSummary:
        if self._lock.locked():
            raise SyncInProgressError("sync is already running")

        async with self._lock:
            started_at = utcnow()
            normalized_channels = self._prepare_channel_usernames(channel_usernames)
            summary = SyncSummary(
                started_at=started_at,
                finished_at=started_at,
                channels_total=len(normalized_channels),
                channels_processed=0,
                posts_created=0,
                posts_updated=0,
                errors=[],
            )

            if not normalized_channels:
                summary.finished_at = utcnow()
                return summary

            async with self.client_service.client() as client:
                for index, username in enumerate(normalized_channels):
                    with self.session_factory() as db:
                        try:
                            created, updated = await self._sync_single_channel(
                                db=db,
                                client=client,
                                username=username,
                                limit=limit or self.settings.fetch_limit,
                            )
                            db.commit()
                            summary.channels_processed += 1
                            summary.posts_created += created
                            summary.posts_updated += updated
                        except Exception as exc:  # noqa: BLE001
                            db.rollback()
                            logger.exception("channel sync failed for %s", username)
                            summary.errors.append(
                                SyncChannelIssue(
                                    username=username,
                                    error=str(exc),
                                ),
                            )

                    if index < len(normalized_channels) - 1 and self.settings.telegram_request_pause_seconds > 0:
                        await asyncio.sleep(self.settings.telegram_request_pause_seconds)

            summary.finished_at = utcnow()
            return summary

    def _prepare_channel_usernames(self, channel_usernames: list[str] | None) -> list[str]:
        #список каналов для синка
        source = channel_usernames or self.settings.telegram_channel_list

        normalized: list[str] = []
        seen: set[str] = set()
        for item in source:
            username = normalize_channel_username(item)
            if not username or username in seen:
                continue
            seen.add(username)
            normalized.append(username)
        return normalized

    async def _sync_single_channel(
        self,
        db: Session,
        client,
        username: str,
        limit: int,
    ) -> tuple[int, int]:
        ensure_configured_channels(db, [username])
        db.flush()

        entity = await client.get_entity(username)
        tracked_channel = db.scalar(
            select(TrackedChannel).where(TrackedChannel.username == username),
        )
        if tracked_channel is None:
            raise RuntimeError(f"tracked channel {username} was not created")

        tracked_channel.title = getattr(entity, "title", username) or username
        tracked_channel.is_active = True
        db.flush()

        messages = await client.get_messages(entity, limit=limit)
        collected_at = utcnow()
        parsed_posts = self._parse_messages(messages, collected_at=collected_at)
        if not parsed_posts:
            return 0, 0

        channel_median_views = self._calculate_channel_median_views(
            db=db,
            tracked_channel_id=tracked_channel.id,
            parsed_posts=parsed_posts,
            collected_at=collected_at,
        )
        self._apply_channel_analytics(
            parsed_posts=parsed_posts,
            channel_median_views=channel_median_views,
            collected_at=collected_at,
        )

        #поиск существующих постов
        message_ids = [item.telegram_message_id for item in parsed_posts]
        existing_posts = db.execute(
            select(ChannelPost).where(
                ChannelPost.tracked_channel_id == tracked_channel.id,
                ChannelPost.telegram_message_id.in_(message_ids),
            ),
        ).scalars()
        existing_map = {item.telegram_message_id: item for item in existing_posts}

        created = 0
        updated = 0

        #апсерт постов
        for item in parsed_posts:
            db_post = existing_map.get(item.telegram_message_id)
            if db_post is None:
                db.add(
                    ChannelPost(
                        tracked_channel_id=tracked_channel.id,
                        telegram_message_id=item.telegram_message_id,
                        message_date=item.message_date,
                        text=item.text,
                        views=item.views,
                        forwards=item.forwards,
                        replies_count=item.replies_count,
                        reactions_total=item.reactions_total,
                        channel_median_views=item.channel_median_views,
                        alert_threshold_views=item.alert_threshold_views,
                        popularity_score=item.popularity_score,
                        is_alert_candidate=item.is_alert_candidate,
                        alerted_at=item.alerted_at,
                        collected_at=item.collected_at,
                        raw_json=item.raw_json,
                    ),
                )
                created += 1
                continue

            db_post.message_date = item.message_date
            db_post.text = item.text
            db_post.views = item.views
            db_post.forwards = item.forwards
            db_post.replies_count = item.replies_count
            db_post.reactions_total = item.reactions_total
            db_post.channel_median_views = item.channel_median_views
            db_post.alert_threshold_views = item.alert_threshold_views
            db_post.popularity_score = item.popularity_score
            db_post.is_alert_candidate = db_post.is_alert_candidate or item.is_alert_candidate
            if item.is_alert_candidate and db_post.alerted_at is None:
                db_post.alerted_at = item.alerted_at
            db_post.collected_at = item.collected_at
            db_post.raw_json = item.raw_json
            updated += 1

        return created, updated

    def _calculate_channel_median_views(
        self,
        db: Session,
        tracked_channel_id: int,
        parsed_posts: list[ParsedTelegramPost],
        collected_at: datetime,
    ) -> float:
        #база канала
        lookback_from = collected_at - timedelta(days=ANALYTICS_LOOKBACK_DAYS)
        existing_rows = db.execute(
            select(
                ChannelPost.telegram_message_id,
                ChannelPost.views,
            ).where(
                ChannelPost.tracked_channel_id == tracked_channel_id,
                ChannelPost.message_date >= lookback_from,
            ),
        ).all()

        views_map = {
            int(message_id): int(views or 0)
            for message_id, views in existing_rows
        }

        for item in parsed_posts:
            if item.message_date < lookback_from:
                continue
            views_map[item.telegram_message_id] = item.views

        return calculate_channel_median_views(list(views_map.values()))

    def _apply_channel_analytics(
        self,
        parsed_posts: list[ParsedTelegramPost],
        channel_median_views: float,
        collected_at: datetime,
    ) -> None:
        #оценка раннего сигнала
        alert_threshold_views = calculate_alert_threshold(channel_median_views)

        for item in parsed_posts:
            age_hours = max((collected_at - item.message_date).total_seconds() / 3600, 0)
            item.channel_median_views = channel_median_views
            item.alert_threshold_views = alert_threshold_views
            item.popularity_score = calculate_popularity_score(
                views=item.views,
                alert_threshold_views=alert_threshold_views,
            )
            item.is_alert_candidate = should_alert_post(
                age_hours=age_hours,
                views=item.views,
                alert_threshold_views=alert_threshold_views,
            )
            item.alerted_at = collected_at if item.is_alert_candidate else None

    def _parse_messages(
        self,
        messages: list[Message],
        collected_at: datetime,
    ) -> list[ParsedTelegramPost]:
        #парсинг сообщений
        parsed_posts: list[ParsedTelegramPost] = []

        for message in messages:
            if self._should_skip_message(message):
                continue

            views = int(getattr(message, "views", 0) or 0)
            forwards = int(getattr(message, "forwards", 0) or 0)
            replies_count = int(getattr(getattr(message, "replies", None), "replies", 0) or 0)
            reactions_total = self._extract_reactions_total(message)
            text = (getattr(message, "message", None) or getattr(message, "raw_text", None) or "").strip()
            normalized_text = text or None

            parsed_posts.append(
                ParsedTelegramPost(
                    telegram_message_id=int(message.id),
                    message_date=message.date,
                    text=normalized_text,
                    views=views,
                    forwards=forwards,
                    replies_count=replies_count,
                    reactions_total=reactions_total,
                    collected_at=collected_at,
                    raw_json=self._safe_raw_message(message),
                ),
            )

        return parsed_posts

    @staticmethod
    def _should_skip_message(message: Message) -> bool:
        if message is None:
            return True
        if getattr(message, "action", None) is not None:
            return True
        if getattr(message, "id", None) is None:
            return True

        text = (getattr(message, "message", None) or getattr(message, "raw_text", None) or "").strip()
        has_media = bool(getattr(message, "media", None))
        return not text and not has_media

    @staticmethod
    def _extract_reactions_total(message: Message) -> int:
        reactions = getattr(message, "reactions", None)
        if reactions is None or getattr(reactions, "results", None) is None:
            return 0

        return sum(int(getattr(result, "count", 0) or 0) for result in reactions.results)

    @staticmethod
    def _safe_raw_message(message: Message) -> dict[str, Any]:
        #без бинарных полей
        return {
            "id": int(message.id),
            "date": message.date.isoformat() if message.date else None,
            "views": int(getattr(message, "views", 0) or 0),
            "forwards": int(getattr(message, "forwards", 0) or 0),
            "has_media": bool(getattr(message, "media", None)),
        }
