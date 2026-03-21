from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
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
    sync_interval_minutes: int = 30
    telegram_channels: list[str] = Field(default_factory=list)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    log_level: str = "INFO"
    fetch_limit: int = 100

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("telegram_channels", "cors_origins", mode="before")
    @classmethod
    def parse_csv_values(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [item.strip() for item in value if item and item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def session_file_path(self) -> Path:
        raw_value = self.telethon_session_name.strip()
        if "/" in raw_value or "\\" in raw_value:
            session_path = Path(raw_value)
        else:
            session_path = self.base_dir / "sessions" / raw_value

        session_path.parent.mkdir(parents=True, exist_ok=True)
        return session_path


@lru_cache
def get_settings() -> Settings:
    return Settings()
