"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings."""

    # Telegram configuration
    telegram_bot_token: str
    telegram_channel_id: Optional[str]
    telegram_alert_chat: Optional[str]

    # OpenRouter (LLM) configuration
    openrouter_api_key: str
    openrouter_model: str

    # OpenClaw configuration
    openclaw_gateway_url: str
    openclaw_enabled: bool

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        self.telegram_alert_chat = os.getenv("TELEGRAM_ALERT_CHAT")

        # OpenRouter
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv(
            "OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free"
        )

        # OpenClaw
        self.openclaw_gateway_url = os.getenv(
            "OPENCLAW_GATEWAY_URL", "http://localhost:3000"
        )
        self.openclaw_enabled = os.getenv("OPENCLAW_ENABLED", "true").lower() == "true"

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate required settings.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")

        if not self.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is required")

        return len(errors) == 0, errors


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Singleton Settings instance
    """
    return Settings()
