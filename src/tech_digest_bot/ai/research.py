"""Research service combining multiple search providers."""

import asyncio
import logging
from typing import Optional

from ..search import DuckDuckGoSearch, OpenClawClient
from .llm import LLMClient

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for researching tech topics using multiple sources."""

    def __init__(
        self,
        llm_client: LLMClient,
        openclaw_client: Optional[OpenClawClient] = None,
    ) -> None:
        """
        Initialize research service.

        Args:
            llm_client: LLM client for generating digests
            openclaw_client: Optional OpenClaw client for browser automation
        """
        self.llm = llm_client
        self.ddg = DuckDuckGoSearch()
        self.openclaw = openclaw_client
        self.openclaw_available = False

    async def initialize(self) -> None:
        """Initialize and check OpenClaw availability."""
        if self.openclaw:
            self.openclaw_available = await self.openclaw.check_availability()
            if self.openclaw_available:
                logger.info("OpenClaw is available - using enhanced research")
            else:
                logger.info("OpenClaw not available - using basic web search only")

    async def research_topic(self, topic: str) -> str:
        """
        Research a tech topic and generate a digest.

        Args:
            topic: Topic to research

        Returns:
            Generated digest as markdown text
        """
        logger.info(f"Researching topic: {topic}")

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
            return f"❌ Could not find information about '{topic}'. Please try a different topic or be more specific."

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
        Research using DuckDuckGo + OpenClaw browser automation.

        Args:
            topic: Topic to research

        Returns:
            Enhanced digest with multi-source data
        """
        if not self.openclaw:
            return await self._research_basic(topic)

        # Run searches in parallel
        web_results, tech_news = await asyncio.gather(
            self.ddg.search(topic, max_results=3),
            self.openclaw.aggregate_tech_news(topic_filter=topic),
            return_exceptions=True,
        )

        # Handle exceptions
        if isinstance(web_results, Exception):
            logger.error(f"Web search failed: {web_results}")
            web_results = []

        if isinstance(tech_news, Exception):
            logger.error(f"OpenClaw aggregation failed: {tech_news}")
            # Fallback to basic research
            return await self._research_basic(topic)

        # Filter relevant items from tech news
        hn_stories = tech_news.get("hackernews", [])[:3]
        gh_repos = tech_news.get("github", [])[:3]
        dev_articles = tech_news.get("devto", [])[:3]

        # Build comprehensive context
        context_parts = ["Web Search Results:"]
        context_parts.extend(
            [f"- {r['title']}: {r['content']}" for r in web_results]
        )

        if hn_stories:
            context_parts.append("\n\nHackerNews Discussions:")
            context_parts.extend(
                [
                    f"- {s['title']} ({s['score']} points) - {s['hn_url']}"
                    for s in hn_stories
                ]
            )

        if gh_repos:
            context_parts.append("\n\nGitHub Trending Projects:")
            context_parts.extend(
                [
                    f"- {r['name']}: {r.get('description', 'No description')} ({r['stars']})"
                    for r in gh_repos
                ]
            )

        if dev_articles:
            context_parts.append("\n\nDev.to Community Articles:")
            context_parts.extend(
                [
                    f"- {a['title']} by {a['author']} ({a['reactions']} reactions)"
                    for a in dev_articles
                ]
            )

        context = "\n".join(context_parts)

        # Enhanced system prompt for multi-source research
        system_prompt = """You are an expert tech digest assistant with access to real-time data from multiple sources including web search, HackerNews, GitHub, and Dev.to.

Create a comprehensive 2-minute digest that:
- Synthesizes information from ALL provided sources
- Highlights trending discussions and projects
- Includes practical code examples or GitHub repos when relevant
- Notes community sentiment from HackerNews discussions
- Provides actionable insights
- Formats beautifully with markdown and emojis
- Cites sources appropriately"""

        # Generate enhanced digest
        digest = await self.llm.generate_digest(
            topic, context, system_prompt=system_prompt, max_tokens=1000
        )
        return digest

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
        return await self.llm.answer_question(question, conversation_history)
