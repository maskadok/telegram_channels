from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.telegram_sync import TelegramSyncService


#подключение к бд
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sync_service(request: Request) -> TelegramSyncService:
    return request.app.state.sync_service
