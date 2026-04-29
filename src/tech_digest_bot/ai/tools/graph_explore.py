"""Graph exploration tool for discovering topic relationships."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import Field

from ...exceptions import GraphError
from .base import TechDigestBaseTool, ToolInput

if TYPE_CHECKING:
    from ...graph.neo4j_store import TechDigestNeo4jStore

logger = logging.getLogger(__name__)


class GraphExploreInput(ToolInput):
    """Input schema for graph exploration."""

    pass


class GraphExploreTool(TechDigestBaseTool):
    """Explore topic relationships in knowledge graph."""

    name: str = "explore_graph_relationships"
    description: str = """Explore relationships between topics in the knowledge graph.

Discovers related topics, topic popularity, and recent articles
discussing the topic. Useful for understanding connections and
trends in the tech ecosystem.

Use this when:
- User asks "what's related to X?"
- Exploring topic connections and trends
- Understanding topic popularity
- Finding similar or connected concepts"""

    args_schema: type[ToolInput] = GraphExploreInput

    # Dependencies
    neo4j_store: TechDigestNeo4jStore = Field(exclude=True)

    async def _arun(self, query: str) -> str:
        """Execute graph exploration."""
        from ...graph.graph_queries import (
            find_related_topics,
            get_recent_articles_on_topic,
            get_topic_popularity,
        )

        try:
            driver = self.neo4j_store.get_driver()
            database = self.neo4j_store.settings.neo4j_database

            # Normalize topic name
            topic_normalized = query.lower().strip()

            # Get popularity
            popularity = await get_topic_popularity(
                driver, topic_normalized, database
            )

            if not popularity:
                return (
                    f"Topic '{query}' not found in knowledge graph. "
                    "It may not have been indexed yet. Try searching the "
                    "web or use a different topic."
                )

            article_count = popularity.get("article_count", 0)
            created_at = popularity.get("created_at", "Unknown")

            # Find related topics
            related_topics = await find_related_topics(
                driver, topic_normalized, database, limit=10
            )

            # Get recent articles
            recent_articles = await get_recent_articles_on_topic(
                driver, topic_normalized, database, limit=5
            )

            # Format response
            return self._format_response(
                query, article_count, created_at, related_topics, recent_articles
            )

        except Exception as e:
            logger.error(f"Graph exploration failed: {e}")
            raise GraphError(f"Topic exploration failed: {e}") from e

    def _format_response(
        self,
        topic: str,
        article_count: int,
        created_at: str,
        related_topics: list[dict],
        recent_articles: list[dict],
    ) -> str:
        """Format exploration results."""
        result = f"**Topic Exploration: {topic.title()}**\n\n"
        result += "**Popularity Metrics:**\n"
        result += f"- Articles discussing this topic: {article_count}\n"
        result += f"- First indexed: {created_at}\n\n"

        if related_topics:
            result += "**Related Topics:**\n"
            for i, rt in enumerate(related_topics, 1):
                name = rt["name"]
                strength = rt["strength"]
                result += (
                    f"{i}. {name.title()} "
                    f"(connection strength: {strength:.2f})\n"
                )
            result += "\n"
        else:
            result += "**Related Topics:** None found\n\n"

        if recent_articles:
            result += "**Recent Articles:**\n"
            for i, article in enumerate(recent_articles, 1):
                title = article["title"]
                url = article["url"]
                result += f"{i}. {title}\n   URL: {url}\n"
            result += "\n"
        else:
            result += "**Recent Articles:** None found\n\n"

        # Add insights
        if article_count > 10:
            result += "💡 **Insight:** This is a popular topic! "
            result += "Consider exploring related topics for more context.\n"
        elif related_topics:
            result += (
                "💡 **Insight:** This topic has strong connections "
                "to other areas. Consider exploring related topics.\n"
            )

        return result
