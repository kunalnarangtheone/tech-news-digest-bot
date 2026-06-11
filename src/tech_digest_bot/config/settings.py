"""Application settings and configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    DEFAULT_GROQ_MODEL,
)


class Settings(BaseSettings):
    """Application configuration settings with Pydantic validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

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
        description="Enable LangChain agent"
    )

    # LangGraph multi-agent Q&A configuration
    use_langgraph: bool = Field(
        default=True,
        description="Enable LangGraph autonomous multi-agent system"
    )
    graph_max_retries: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum critic retries for low-confidence answers"
    )
    graph_confidence_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to avoid retry"
    )

    # Langfuse observability (optional)
    langfuse_public_key: str | None = Field(
        default=None,
        description="Langfuse public key for tracing (optional)"
    )
    langfuse_secret_key: str | None = Field(
        default=None,
        description="Langfuse secret key for tracing (optional)"
    )

    # API configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API server port"
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="CORS allowed origins"
    )

    # Session configuration
    session_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,  # Max 1 week
        description="Session TTL in hours"
    )

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
    # Pydantic will raise ValidationError if GROQ_API_KEY is missing
    # This is caught by the caller
    return Settings()  # type: ignore[call-arg]
