from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    database_url: str = "postgresql+psycopg2://dailyflow:dailyflow@localhost:5432/dailyflow"

    timezone: str = "America/Sao_Paulo"
    link_code_ttl_minutes: int = 15

    morning_summary_hour: int = 7
    evening_summary_hour: int = 21
    habit_reminder_hour: int = 18
    due_soon_window_minutes: int = 120
    poll_interval_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
