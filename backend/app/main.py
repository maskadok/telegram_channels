from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.scheduler.scheduler import SyncScheduler
from app.services.channel_service import ensure_configured_channels
from app.services.telegram_sync import TelegramSyncService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)

    sync_service = TelegramSyncService(settings=settings, session_factory=SessionLocal)
    scheduler = SyncScheduler(settings=settings, sync_service=sync_service)

    app.state.settings = settings
    app.state.sync_service = sync_service
    app.state.scheduler = scheduler

    with SessionLocal() as db:
        ensure_configured_channels(db, settings.telegram_channel_list)
        db.commit()

    #запуск планировщика
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()


settings = get_settings()

app = FastAPI(
    title="Telegram Analytics MVP",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
