"""Dependency Injection container for Tech Digest Bot."""

from dependency_injector import containers, providers

from .ai.llm import LLMClient
from .ai.research import ResearchService
from .config import get_settings
from .graph.neo4j_store import TechDigestNeo4jStore


class ApplicationContainer(containers.DeclarativeContainer):
    """Application dependency injection container."""

    # Configuration
    config = providers.Singleton(get_settings)

    # LLM Client (Groq)
    llm_client = providers.Singleton(
        LLMClient,
        model=config.provided.groq_model,
        api_key=config.provided.groq_api_key,
    )

    # Neo4j Store (lazy initialization for agent)
    neo4j_store = providers.Singleton(
        TechDigestNeo4jStore,
        settings=config,
    )

    # Research Service
    research_service = providers.Singleton(
        ResearchService,
        llm_client=llm_client,
        use_agent=config.provided.use_langchain_agent,
        settings=config,
    )


def create_container() -> ApplicationContainer:
    """
    Create and configure the DI container.

    Returns:
        Configured ApplicationContainer instance
    """
    container = ApplicationContainer()

    # Wire dependencies to modules that need injection
    container.wire(modules=[
        "tech_digest_bot.bot.app",
    ])

    return container
