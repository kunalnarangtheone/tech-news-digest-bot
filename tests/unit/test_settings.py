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
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "false")

        settings = Settings()
        assert settings.telegram_bot_token == "test-token"
        assert settings.groq_api_key == "test-groq-key"
        assert settings.use_langchain_agent is False

    def test_missing_telegram_token_raises(self, monkeypatch):
        """Test missing required token."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

        with pytest.raises(ValidationError) as exc:
            Settings(_env_file=None)  # Don't load from .env file

        assert "telegram_bot_token" in str(exc.value).lower()

    def test_missing_groq_api_key_raises(self, monkeypatch):
        """Test missing required Groq API key."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        with pytest.raises(ValidationError) as exc:
            Settings(_env_file=None)  # Don't load from .env file

        assert "groq_api_key" in str(exc.value).lower()

    def test_agent_requires_neo4j_password(self, monkeypatch):
        """Test Neo4j password required when agent enabled."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "true")
        monkeypatch.setenv("NEO4J_PASSWORD", "")

        with pytest.raises((ValidationError, SettingsValidationError)):
            Settings()

    def test_default_values(self, monkeypatch):
        """Test default configuration values."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "false")

        settings = Settings()
        assert settings.groq_model == "llama-3.3-70b-versatile"
        assert settings.embedding_dimension == 384
        assert settings.use_langchain_agent is False

    def test_type_coercion(self, monkeypatch):
        """Test Pydantic type coercion."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "1024")  # String
        monkeypatch.setenv("USE_LANGCHAIN_AGENT", "true")  # String
        monkeypatch.setenv("NEO4J_PASSWORD", "test-pass")

        settings = Settings()
        assert isinstance(settings.embedding_dimension, int)
        assert settings.embedding_dimension == 1024
        assert settings.use_langchain_agent is True
