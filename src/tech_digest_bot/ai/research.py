"""Research service combining multiple search providers."""

import logging
from typing import Optional, TYPE_CHECKING

from ..search import DuckDuckGoSearch
from .llm import LLMClient

if TYPE_CHECKING:
    from .agent import TechIntelligenceAgent
    from ..config.settings import Settings

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for researching tech topics using multiple sources."""

    def __init__(
        self,
        llm_client: LLMClient,
        use_agent: bool = True,
        settings: Optional["Settings"] = None,
    ) -> None:
        """
        Initialize research service.

        Args:
            llm_client: LLM client for generating digests
            use_agent: Whether to use LangChain agent (default: True)
            settings: Settings object for agent initialization
        """
        self.llm = llm_client
        self.ddg = DuckDuckGoSearch()

        # LangChain agent integration
        self.use_agent = use_agent
        self.settings = settings
        self.agent: Optional["TechIntelligenceAgent"] = None
        self.neo4j_store = None

    async def initialize(self) -> None:
        """Initialize LangChain agent."""
        # Initialize LangChain agent with Neo4j
        if self.use_agent and self.settings:
            try:
                from ..graph.neo4j_store import TechDigestNeo4jStore
                from .agent import TechIntelligenceAgent

                # Initialize Neo4j vector store
                logger.info("Initializing Neo4j store for agent...")
                self.neo4j_store = TechDigestNeo4jStore(self.settings)

                # Initialize LangChain agent
                logger.info("Initializing LangChain agent...")
                self.agent = TechIntelligenceAgent(
                    self.neo4j_store, self.settings, self.llm
                )

                logger.info(
                    "✓ LangChain agent initialized successfully"
                )
            except Exception as e:
                logger.exception(
                    f"Failed to initialize LangChain agent: {e}"
                )
                self.use_agent = False
                self.agent = None

    async def research_topic(self, topic: str) -> str:
        """
        Research a tech topic and generate a digest.

        Priority:
        1. LangChain agent (if enabled) - intelligent tool selection
        2. Basic DuckDuckGo - fallback

        Args:
            topic: Topic to research

        Returns:
            Generated digest as markdown text
        """
        logger.info("Researching topic: %s", topic)

        # Try LangChain agent first
        if self.use_agent and self.agent:
            try:
                logger.info("Using LangChain agent for research")
                result = await self.agent.research(topic)
                return result["output"]
            except Exception as e:
                logger.exception(
                    f"LangChain agent failed: {e}"
                )
                # Fall through to basic search

        # Fallback to basic DuckDuckGo
        return await self._research_basic(topic)

    async def _research_basic(self, topic: str) -> str:
        """
        Research using only DuckDuckGo web search.

        Args:
            topic: Topic to research

        Returns:
            Generated digest
        """
        # Search the web
        search_results = await self.ddg.search(topic, max_results=5)

        if not search_results:
            return (
                f"❌ Could not find information about '{topic}'. "
                "Please try a different topic or be more specific."
            )

        # Prepare context from search results
        context = "\n\n".join(
            [
                f"Source: {r['title']}\nURL: {r['url']}\n{r['content']}"
                for r in search_results
            ]
        )

        # Generate digest
        digest = await self.llm.generate_digest(topic, context)
        return digest

    async def answer_followup(
        self, question: str, conversation_history: list[dict[str, str]]
    ) -> str:
        """
        Answer a follow-up question.

        Priority:
        1. LangChain agent (if enabled) - context-aware
        2. Basic LLM - fallback

        Args:
            question: User's question
            conversation_history: Previous conversation messages

        Returns:
            Answer text
        """
        # Try LangChain agent first
        if self.use_agent and self.agent:
            try:
                logger.info("Using LangChain agent for follow-up")
                result = await self.agent.answer_followup(
                    question, conversation_history
                )
                return result["output"]
            except Exception as e:
                logger.exception(f"Agent follow-up failed: {e}")
                # Fall through to basic LLM

        # Fallback to basic LLM
        return await self.llm.answer_question(
            question, conversation_history
        )

    async def cleanup(self):
        """Cleanup resources (Neo4j connection, etc.)."""
        if self.neo4j_store:
            await self.neo4j_store.close()
            logger.info("Neo4j store closed")
