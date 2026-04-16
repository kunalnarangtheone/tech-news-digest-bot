"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from tech_digest_bot.config import Settings


def test_settings_loads_from_env():
    """Test that settings load from environment variables."""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
            "OPENROUTER_MODEL": "test_model",
            "OPENCLAW_ENABLED": "false",
        },
    ):
        settings = Settings()
        assert settings.telegram_bot_token == "test_token"
        assert settings.openrouter_api_key == "test_key"
        assert settings.openrouter_model == "test_model"
        assert settings.openclaw_enabled is False


def test_settings_validation_success():
    """Test that validation passes with required settings."""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "OPENROUTER_API_KEY": "test_key",
        },
    ):
        settings = Settings()
        is_valid, errors = settings.validate()
        assert is_valid is True
        assert len(errors) == 0


def test_settings_validation_failure():
    """Test that validation fails with missing settings."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        is_valid, errors = settings.validate()
        assert is_valid is False
        assert len(errors) == 2
        assert "TELEGRAM_BOT_TOKEN is required" in errors
        assert "OPENROUTER_API_KEY is required" in errors


def test_settings_default_values():
    """Test that settings have correct default values."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert settings.openrouter_model == "google/gemini-2.0-flash-exp:free"
        assert settings.openclaw_gateway_url == "http://localhost:3000"
        assert settings.openclaw_enabled is True
