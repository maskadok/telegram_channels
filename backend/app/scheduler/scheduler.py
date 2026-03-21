from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings
from app.scheduler.jobs import run_periodic_sync
from app.services.telegram_sync import TelegramSyncService


class SyncScheduler:
    def __init__(self, settings: Settings, sync_service: TelegramSyncService) -> None:
        self.settings = settings
        self.sync_service = sync_service
        self._scheduler = AsyncIOScheduler()
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        #запуск по интервалу
        self._scheduler.add_job(
            run_periodic_sync,
            "interval",
            minutes=self.settings.sync_interval_minutes,
            args=[self.sync_service],
            id="telegram-sync",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60,
        )
        self._scheduler.start()
        self._started = True

    def shutdown(self) -> None:
        if not self._started:
            return

        self._scheduler.shutdown(wait=False)
        self._started = False

    @property
    def is_running(self) -> bool:
        return self._started
