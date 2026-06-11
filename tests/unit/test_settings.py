"""Unit tests for Pydantic settings."""

import pytest
from pydantic import ValidationError

from tech_digest_bot.config import Settings
from tech_digest_bot.exceptions import SettingsValidationError


@pytest.mark.unit
class TestSettings:
    """Test Settings validation."""

    def test_minimal_valid_settings(self, monkeypatch):
        """Test with minimal required settings."""
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "false")

        settings = Settings()
        assert settings.groq_api_key == "test-groq-key"
        assert settings.use_langchain_agent is False

    def test_missing_groq_api_key_raises(self, monkeypatch):
        """Test missing required Groq API key."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        with pytest.raises(ValidationError) as exc:
            Settings(_env_file=None)  # Don't load from .env file

        assert "groq_api_key" in str(exc.value).lower()

    def test_default_values(self, monkeypatch):
        """Test default configuration values."""
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "false")

        settings = Settings()
        assert settings.groq_model == "llama-3.3-70b-versatile"
        assert settings.use_langchain_agent is False
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.session_ttl_hours == 24

    def test_type_coercion(self, monkeypatch):
        """Test Pydantic type coercion."""
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "true")  # String

        settings = Settings()
        assert settings.use_langchain_agent is True

    def test_api_configuration(self, monkeypatch):
        """Test API-specific configuration."""
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "false")
        monkeypatch.setenv("API_HOST", "127.0.0.1")
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("SESSION_TTL_HOURS", "48")

        settings = Settings()
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000
        assert settings.session_ttl_hours == 48
