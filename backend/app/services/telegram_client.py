from contextlib import asynccontextmanager

from telethon import TelegramClient
from telethon.errors import AuthKeyError

from app.core.config import Settings


class TelegramAuthError(RuntimeError):
    pass


#сервис телеграма
class TelegramClientService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @asynccontextmanager
    async def client(self):
        if not self.settings.telegram_api_id or not self.settings.telegram_api_hash:
            raise TelegramAuthError("telegram credentials are not configured")

        client = TelegramClient(
            str(self.settings.session_file_path),
            self.settings.telegram_api_id,
            self.settings.telegram_api_hash,
        )

        try:
            await client.connect()
            #проверка сессии
            if not await client.is_user_authorized():
                raise TelegramAuthError(
                    "telethon session is not authorized, run the session bootstrap script first",
                )
            yield client
        except AuthKeyError as exc:
            raise TelegramAuthError("telethon session is invalid, recreate it") from exc
        finally:
            await client.disconnect()
