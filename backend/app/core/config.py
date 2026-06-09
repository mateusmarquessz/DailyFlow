from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DailyFlow API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg2://dailyflow:dailyflow@localhost:5432/dailyflow"

    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    password_reset_token_expire_minutes: int = 60

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "no-reply@dailyflow.app"
    frontend_url: str = "http://localhost:5173"

    telegram_bot_token: str | None = None
    telegram_bot_username: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
