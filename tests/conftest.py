"""Pytest fixtures and configuration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tech_digest_bot.ai.agent import TechIntelligenceAgent
from tech_digest_bot.ai.llm import LLMClient
from tech_digest_bot.config import Settings
from tech_digest_bot.graph.neo4j_store import TechDigestNeo4jStore

# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_settings() -> Settings:
    """Mock settings for testing (no validation)."""
    with patch.dict('os.environ', {
        'TELEGRAM_BOT_TOKEN': 'test-token-123',
        'NEO4J_PASSWORD': 'test-password',
        'GROQ_API_KEY': 'test-groq-key',
        'GROQ_MODEL': 'llama-3.3-70b-versatile',
        'USE_LANGCHAIN_AGENT': 'false',  # Disable agent by default
    }):
        return Settings()


@pytest.fixture
def real_settings() -> Settings:
    """Real settings from .env (for integration tests)."""
    return Settings()


# ============================================================================
# LLM Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_client() -> LLMClient:
    """Mock LLM client with predictable responses."""
    client = LLMClient(model="test-model", api_key="test-key")

    # Mock the OpenAI client
    client.client = MagicMock()

    # Mock digest generation
    async def mock_generate_digest(topic, context, **kwargs):
        return f"**{topic}**\\n\\nMocked digest content"

    # Mock question answering
    async def mock_answer_question(question, history, **kwargs):
        return f"Mocked answer to: {question}"

    client.generate_digest = AsyncMock(side_effect=mock_generate_digest)
    client.answer_question = AsyncMock(side_effect=mock_answer_question)

    return client


# ============================================================================
# Neo4j Fixtures
# ============================================================================

@pytest.fixture
def mock_neo4j_store(mock_settings) -> TechDigestNeo4jStore:
    """Mock Neo4j store (no real connection)."""
    store = MagicMock(spec=TechDigestNeo4jStore)
    store.settings = mock_settings

    # Mock search methods
    store.hybrid_search = AsyncMock(return_value=[
        {
            "id": "test-article-1",
            "title": "Test Article",
            "url": "https://example.com",
            "content": "Test content",
            "snippet": "Test snippet",
            "bm25_score": 5.0,
        }
    ])

    store.bm25_search = AsyncMock(return_value=[])
    store.add_documents = AsyncMock(return_value=["doc-id-1", "doc-id-2"])

    # Mock driver
    mock_driver = AsyncMock()
    store.get_driver = MagicMock(return_value=mock_driver)
    store.close = AsyncMock()

    return store


# ============================================================================
# Agent Fixtures
# ============================================================================

@pytest.fixture
def mock_agent(mock_neo4j_store, mock_settings, mock_llm_client):
    """Mock agent with mocked dependencies."""
    agent = MagicMock(spec=TechIntelligenceAgent)

    agent.research = AsyncMock(return_value={
        "output": "Mocked agent research result",
        "intermediate_steps": [],
    })

    agent.answer_followup = AsyncMock(return_value={
        "output": "Mocked followup answer",
        "intermediate_steps": [],
    })

    return agent


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests (require services)"
    )
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests (full system)"
    )
