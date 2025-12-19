"""Configuration from environment variables."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Bot configuration."""
    
    # Telegram
    bot_token: str
    webhook_secret: str
    webhook_path: str
    webhook_base_url: str  # e.g., https://dev.x5teamintern.ru
    
    # API
    api_base_url: str
    
    # App
    environment: str
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables."""
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN_CANDIDATE") or os.getenv("TELEGRAM_BOT_TOKEN", ""),
            webhook_secret=os.getenv("WEBHOOK_SECRET_CANDIDATE") or os.getenv("WEBHOOK_SECRET", ""),
            webhook_path=os.getenv("WEBHOOK_PATH", "/tg/candidate"),
            webhook_base_url=os.getenv("WEBHOOK_BASE_URL", ""),  # Required for webhook registration
            api_base_url=os.getenv("API_BASE_URL", "http://core-api:8000"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    @property
    def webhook_url(self) -> str:
        """Full webhook URL for Telegram."""
        return f"{self.webhook_base_url}{self.webhook_path}/{self.webhook_secret}"


config = Config.from_env()

