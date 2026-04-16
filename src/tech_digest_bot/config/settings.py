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

    # Ollama (LLM) configuration
    ollama_base_url: str
    ollama_model: str

    # OpenClaw configuration
    openclaw_gateway_url: str
    openclaw_enabled: bool

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        self.telegram_alert_chat = os.getenv("TELEGRAM_ALERT_CHAT")

        # Ollama
        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434/v1"
        )
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        # OpenClaw
        self.openclaw_gateway_url = os.getenv(
            "OPENCLAW_GATEWAY_URL", "http://localhost:18789"
        )
        enabled = os.getenv("OPENCLAW_ENABLED", "true").lower()
        self.openclaw_enabled = enabled == "true"

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate required settings.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")

        return len(errors) == 0, errors


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Singleton Settings instance
    """
    return Settings()
