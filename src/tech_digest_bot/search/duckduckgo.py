"""DuckDuckGo search provider."""

import logging
from typing import Any

from duckduckgo_search import DDGS

from ..models import SearchResult

logger = logging.getLogger(__name__)


class DuckDuckGoSearch:
    """DuckDuckGo web search client."""

    def __init__(self) -> None:
        """Initialize DuckDuckGo search client."""
        self.client = DDGS()

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """
        Search the web using DuckDuckGo.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        try:
            search_results = self.client.text(
                keywords=query,
                max_results=max_results,
                region="wt-wt",  # Global results
            )

            results: list[SearchResult] = []
            for result in search_results:
                results.append(
                    SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        content=result.get("body", ""),
                    )
                )

            logger.info(f"Found {len(results)} search results for: {query}")
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
