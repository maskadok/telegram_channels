from functools import lru_cache
from pathlib import Path

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


#настройки приложения
class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/telegram_analytics"
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str | None = None
    telethon_session_name: str = "telegram_user"
    telethon_session_dir: str | None = None
    sync_interval_minutes: int = 120
    telegram_channels: str = "tproger,habr_com"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    fetch_limit: int = 30
    telegram_request_pause_seconds: int = 3

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("telegram_channels", "cors_origins", mode="before")
    @classmethod
    def normalize_csv_value(cls, value: str | list[str] | None) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return ",".join(item.strip() for item in value if item and item.strip())
        return value.strip()

    @field_validator(
        "telegram_api_id",
        "app_port",
        "sync_interval_minutes",
        "fetch_limit",
        "telegram_request_pause_seconds",
        mode="before",
    )
    @classmethod
    def normalize_int_value(cls, value: str | int | None, info: ValidationInfo) -> int:
        defaults = {
            "telegram_api_id": 0,
            "app_port": 8000,
            "sync_interval_minutes": 120,
            "fetch_limit": 30,
            "telegram_request_pause_seconds": 3,
        }
        if value is None:
            return defaults[info.field_name]
        if isinstance(value, str) and not value.strip():
            return defaults[info.field_name]
        return int(value)

    @staticmethod
    def _parse_csv(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def telegram_channel_list(self) -> list[str]:
        return self._parse_csv(self.telegram_channels)

    @property
    def cors_origin_list(self) -> list[str]:
        return self._parse_csv(self.cors_origins)

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def session_file_path(self) -> Path:
        raw_value = self.telethon_session_name.strip()
        if "/" in raw_value or "\\" in raw_value:
            session_path = Path(raw_value)
        elif self.telethon_session_dir:
            session_path = Path(self.telethon_session_dir) / raw_value
        else:
            session_path = self.base_dir / "sessions" / raw_value

        session_path.parent.mkdir(parents=True, exist_ok=True)
        return session_path


@lru_cache
def get_settings() -> Settings:
    return Settings()
