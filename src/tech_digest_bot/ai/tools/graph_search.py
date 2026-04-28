"""Knowledge graph search tool using BM25 + graph relationships."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import Field

from .base import TechDigestBaseTool, ToolInput
from ...config.constants import MIN_BM25_SCORE_THRESHOLD, STOP_WORDS
from ...exceptions import GraphError

if TYPE_CHECKING:
    from ...graph.neo4j_store import TechDigestNeo4jStore

logger = logging.getLogger(__name__)


class GraphSearchInput(ToolInput):
    """Input schema for graph search."""

    pass


class GraphSearchTool(TechDigestBaseTool):
    """Search knowledge graph for previously indexed articles."""

    name: str = "search_knowledge_graph"
    description: str = """Search the knowledge graph for articles related to a query.

Uses BM25 full-text search for keyword relevance, then enhances
results with graph relationships (topics, related articles).

Use this when:
- User asks about topics you might have seen before
- Looking for previously indexed content
- Exploring relationships between known topics"""

    args_schema: type[ToolInput] = GraphSearchInput

    # Dependencies
    neo4j_store: "TechDigestNeo4jStore" = Field(exclude=True)

    async def _arun(self, query: str) -> str:
        """Execute graph search with filtering."""
        from ...graph.graph_queries import (
            get_related_topics,
            get_related_articles,
        )

        try:
            # Perform hybrid search
            results = await self.neo4j_store.hybrid_search(query, k=5)

            # Filter results for relevance
            filtered_results = self._filter_results(query, results)

            if not filtered_results:
                return (
                    "No relevant articles found in knowledge graph. "
                    "Try searching the web for current information."
                )

            # Format with graph context
            formatted = await self._format_results(filtered_results)

            summary = (
                f"Found {len(filtered_results)} relevant articles in "
                f"knowledge graph:\n\n"
            )
            return summary + "\n\n".join(formatted)

        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            raise GraphError(f"Knowledge graph search failed: {e}")

    def _filter_results(self, query: str, results: list[dict]) -> list[dict]:
        """Filter results by score and query term matching."""
        # Extract query terms
        query_terms = [
            term.lower().strip()
            for term in query.split()
            if term.lower().strip() not in STOP_WORDS and len(term) > 2
        ]

        filtered = []
        for result in results:
            bm25_score = result.get("bm25_score", 0.0)
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()

            # Filter 1: Score threshold
            if bm25_score < MIN_BM25_SCORE_THRESHOLD:
                logger.debug(
                    f"Filtered low score ({bm25_score:.2f}): "
                    f"{result.get('title')}"
                )
                continue

            # Filter 2: Term verification
            term_found = any(
                term in title or term in content for term in query_terms
            )

            if not term_found and query_terms:
                logger.debug(f"Filtered (no terms): {result.get('title')}")
                continue

            filtered.append(result)

        return filtered

    async def _format_results(self, results: list[dict]) -> list[str]:
        """Format results with graph context."""
        from ...graph.graph_queries import (
            get_related_topics,
            get_related_articles,
        )

        formatted = []
        driver = self.neo4j_store.get_driver()

        for i, result in enumerate(results, 1):
            article_id = result.get("id")
            title = result.get("title", "Untitled")
            url = result.get("url", "N/A")
            snippet = result.get("snippet", "")[:200]
            bm25_score = result.get("bm25_score", 0.0)

            # Get topics
            topics = await get_related_topics(
                driver, article_id, self.neo4j_store.settings.neo4j_database
            )

            # Count related articles
            related_count = 0
            if topics:
                related_articles = await get_related_articles(
                    driver,
                    topics[0],
                    self.neo4j_store.settings.neo4j_database,
                    limit=3,
                )
                related_count = len(
                    [a for a in related_articles if a["id"] != article_id]
                )

            result_text = f"""
**{i}. {title}** (relevance: {bm25_score:.2f})
URL: {url}
Snippet: {snippet}...
Topics: {', '.join(topics[:5]) if topics else 'None'}
Related Articles: {related_count}
"""
            formatted.append(result_text.strip())

        return formatted
