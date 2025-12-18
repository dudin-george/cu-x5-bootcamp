"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Environment
    environment: str = "dev"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/recruitment_db"

    # Security (JWT - not used currently)
    secret_key: str = "not-used-placeholder-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Telegram
    telegram_bot_token_candidate: str = ""
    telegram_bot_token_hm: str = ""

    # ML Service
    ml_service_url: str = "http://localhost:8001"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    frontend_url: str = "http://localhost:5173"


settings = Settings()
