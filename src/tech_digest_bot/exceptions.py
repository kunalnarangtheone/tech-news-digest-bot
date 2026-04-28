"""Custom exception hierarchy for Tech Digest Bot."""


class TechDigestBotError(Exception):
    """Base exception for all Tech Digest Bot errors."""
    pass


# Configuration Errors
class ConfigurationError(TechDigestBotError):
    """Raised when configuration is invalid or missing."""
    pass


class SettingsValidationError(ConfigurationError):
    """Raised when settings validation fails."""
    pass


# LLM Errors
class LLMError(TechDigestBotError):
    """Base exception for LLM-related errors."""
    pass


class LLMGenerationError(LLMError):
    """Raised when LLM generation fails."""
    pass


class LLMConnectionError(LLMError):
    """Raised when cannot connect to LLM service."""
    pass


# Search Errors
class SearchError(TechDigestBotError):
    """Base exception for search-related errors."""
    pass


class WebSearchError(SearchError):
    """Raised when web search fails."""
    pass


# Graph/Neo4j Errors
class GraphError(TechDigestBotError):
    """Base exception for graph database errors."""
    pass


class Neo4jConnectionError(GraphError):
    """Raised when cannot connect to Neo4j."""
    pass


class Neo4jQueryError(GraphError):
    """Raised when Neo4j query fails."""
    pass


class EmbeddingError(GraphError):
    """Raised when embedding generation fails."""
    pass


# Agent Errors
class AgentError(TechDigestBotError):
    """Base exception for agent-related errors."""
    pass


class ToolExecutionError(AgentError):
    """Raised when agent tool execution fails."""
    pass


class AgentInitializationError(AgentError):
    """Raised when agent cannot be initialized."""
    pass


# Research Service Errors
class ResearchError(TechDigestBotError):
    """Base exception for research service errors."""
    pass


class NoResultsError(ResearchError):
    """Raised when no results found for query."""
    pass


class IngestionError(ResearchError):
    """Raised when cannot ingest content to graph."""
    pass
