"""Research service combining multiple search providers."""

import logging
from typing import Optional

from ..search import DuckDuckGoSearch, OpenClawCLIClient
from .llm import LLMClient

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for researching tech topics using multiple sources."""

    def __init__(
        self,
        llm_client: LLMClient,
        openclaw_client: Optional[OpenClawCLIClient] = None,
    ) -> None:
        """
        Initialize research service.

        Args:
            llm_client: LLM client for generating digests
            openclaw_client: Optional OpenClaw CLI client for agent queries
        """
        self.llm = llm_client
        self.ddg = DuckDuckGoSearch()
        self.openclaw = openclaw_client
        self.openclaw_available = False

    async def initialize(self) -> None:
        """Initialize and check OpenClaw availability."""
        if self.openclaw:
            available = await self.openclaw.check_availability()
            self.openclaw_available = available
            if self.openclaw_available:
                logger.info(
                    "OpenClaw is available - using enhanced research"
                )
            else:
                logger.info(
                    "OpenClaw not available - using basic web search only"
                )

    async def research_topic(self, topic: str) -> str:
        """
        Research a tech topic and generate a digest.

        Args:
            topic: Topic to research

        Returns:
            Generated digest as markdown text
        """
        logger.info("Researching topic: %s", topic)

        if self.openclaw_available and self.openclaw:
            return await self._research_with_openclaw(topic)
        else:
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

    async def _research_with_openclaw(self, topic: str) -> str:
        """
        Research using OpenClaw Agent (uses GitHub Copilot).

        Args:
            topic: Topic to research

        Returns:
            Enhanced digest with OpenClaw agent research
        """
        if not self.openclaw:
            return await self._research_basic(topic)

        # Use OpenClaw agent to do the full research AND digest generation
        logger.info("Requesting OpenClaw agent to research and generate digest: %s", topic)

        prompt = f"""Research the following tech topic and create a comprehensive 2-minute digest:

Topic: {topic}

Please:
1. Search for current information from HackerNews, GitHub, Dev.to, and web
2. Create a concise digest (200-300 words) covering:
   - Brief overview (1-2 sentences)
   - Most important points in bullet format
   - Recent developments or trends if relevant
   - Practical examples or use cases
   - 2-3 source URLs at the end

Format in markdown with emojis for visual appeal. Keep it engaging but accurate."""

        result = await self.openclaw.ask_agent(prompt, timeout=90)

        if result.get("success") and result.get("response"):
            return result["response"]

        # Fallback to basic research if OpenClaw fails
        logger.warning(
            "OpenClaw agent failed, falling back to basic research: %s",
            result.get("error", "Unknown error")
        )
        return await self._research_basic(topic)

    async def answer_followup(
        self, question: str, conversation_history: list[dict[str, str]]
    ) -> str:
        """
        Answer a follow-up question.

        Args:
            question: User's question
            conversation_history: Previous conversation messages

        Returns:
            Answer text
        """
        # Use OpenClaw agent if available for follow-up questions too
        if self.openclaw_available and self.openclaw:
            # Convert history to context
            context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-6:]  # Last 3 exchanges
            ])

            prompt = f"""Based on this conversation history:

{context}

User's follow-up question: {question}

Please provide a concise, helpful answer (under 150 words). Use markdown formatting."""

            result = await self.openclaw.ask_agent(prompt, timeout=60)

            if result.get("success") and result.get("response"):
                return result["response"]

        # Fallback to LLM
        return await self.llm.answer_question(question, conversation_history)
