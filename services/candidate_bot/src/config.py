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
    
    # API
    api_base_url: str
    
    # App
    environment: str
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables.
        
        GitHub secrets:
        - TELEGRAM_BOT_TOKEN_CANDIDATE (prod) / TELEGRAM_BOT_TOKEN (dev fallback)
        - WEBHOOK_SECRET_CANDIDATE (prod) / WEBHOOK_SECRET (dev fallback)
        """
        return cls(
            # Try prod name first, fallback to dev name
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN_CANDIDATE") or os.getenv("TELEGRAM_BOT_TOKEN", ""),
            webhook_secret=os.getenv("WEBHOOK_SECRET_CANDIDATE") or os.getenv("WEBHOOK_SECRET", ""),
            webhook_path=os.getenv("WEBHOOK_PATH", "/tg/candidate"),
            api_base_url=os.getenv("API_BASE_URL", "http://core-api:8000"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    @property
    def webhook_url(self) -> str:
        """Full webhook path with secret."""
        return f"{self.webhook_path}/{self.webhook_secret}"


config = Config.from_env()

