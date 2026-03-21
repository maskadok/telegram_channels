import asyncio
from pathlib import Path

from telethon import TelegramClient

from app.core.config import get_settings


#авторизация telethon
async def run_interactive_login() -> Path:
    settings = get_settings()
    session_path = settings.session_file_path

    if not settings.telegram_api_id or not settings.telegram_api_hash:
        raise RuntimeError("telegram credentials are not configured")

    async with TelegramClient(
        str(session_path),
        settings.telegram_api_id,
        settings.telegram_api_hash,
    ) as client:
        await client.start(phone=settings.telegram_phone or None)
        me = await client.get_me()
        print(f"authorized as: {getattr(me, 'username', None) or me.id}")
        print(f"session file: {session_path}.session")

    return session_path


def main() -> None:
    asyncio.run(run_interactive_login())


if __name__ == "__main__":
    main()
