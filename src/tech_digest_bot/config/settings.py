"""Application settings and configuration."""

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..exceptions import SettingsValidationError
from .constants import (
    DEFAULT_EMBEDDING_DIMENSION,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_GROQ_MODEL,
    DEFAULT_NEO4J_DATABASE,
    DEFAULT_NEO4J_URI,
    DEFAULT_NEO4J_USER,
)


class Settings(BaseSettings):
    """Application configuration settings with Pydantic validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram configuration
    telegram_bot_token: str = Field(
        ...,  # Required
        description="Telegram bot token from BotFather"
    )
    telegram_channel_id: str | None = Field(default=None)
    telegram_alert_chat: str | None = Field(default=None)

    # Groq LLM configuration
    groq_api_key: str = Field(
        ...,  # Required
        description="Groq API key from console.groq.com"
    )
    groq_model: str = Field(
        default=DEFAULT_GROQ_MODEL,
        description="Groq model identifier"
    )

    # LangChain Agent configuration
    use_langchain_agent: bool = Field(
        default=True,
        description="Enable LangChain agent with Neo4j"
    )

    # Neo4j Aura configuration
    neo4j_uri: str = Field(
        default=DEFAULT_NEO4J_URI,
        description="Neo4j connection URI"
    )
    neo4j_user: str = Field(
        default=DEFAULT_NEO4J_USER,
        description="Neo4j username"
    )
    neo4j_password: str = Field(
        default="",
        description="Neo4j password"
    )
    neo4j_database: str = Field(
        default=DEFAULT_NEO4J_DATABASE,
        description="Neo4j database name"
    )

    # Embedding configuration
    embedding_model: str = Field(
        default=DEFAULT_EMBEDDING_MODEL,
        description="Embedding model name"
    )
    embedding_dimension: int = Field(
        default=DEFAULT_EMBEDDING_DIMENSION,
        ge=1,
        le=4096,
        description="Embedding vector dimension"
    )

    @model_validator(mode='after')
    def validate_agent_config(self) -> Settings:
        """Validate Neo4j password when agent is enabled."""
        if self.use_langchain_agent and not self.neo4j_password:
            raise SettingsValidationError(
                "NEO4J_PASSWORD is required when USE_LANGCHAIN_AGENT=true"
            )
        return self

    def validate(self) -> tuple[bool, list[str]]:
        """
        Legacy validate method for backward compatibility.

        Pydantic validation happens automatically on instantiation.
        This method always returns (True, []) for valid instances.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        return True, []


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Singleton Settings instance
    """
    return Settings()
