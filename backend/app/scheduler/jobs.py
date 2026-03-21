import logging

from app.services.telegram_sync import SyncInProgressError, TelegramSyncService

logger = logging.getLogger(__name__)


async def run_periodic_sync(sync_service: TelegramSyncService) -> None:
    try:
        summary = await sync_service.sync_channels()
        logger.info(
            "sync finished: channels=%s processed=%s created=%s updated=%s errors=%s",
            summary.channels_total,
            summary.channels_processed,
            summary.posts_created,
            summary.posts_updated,
            len(summary.errors),
        )
    except SyncInProgressError:
        logger.info("sync skipped because another run is still active")
    except Exception:  # noqa: BLE001
        logger.exception("scheduled sync failed")
