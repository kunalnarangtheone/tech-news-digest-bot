"""DuckDuckGo search provider."""

import logging
from typing import TypedDict

from ddgs import DDGS

logger = logging.getLogger(__name__)


class SearchResult(TypedDict):
    """Search result data structure."""

    title: str
    url: str
    content: str


class DuckDuckGoSearch:
    """DuckDuckGo web search client."""

    def __init__(self) -> None:
        """Initialize DuckDuckGo search client."""
        self.client = DDGS()

    async def search(
        self, query: str, max_results: int = 5
    ) -> list[SearchResult]:
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
                query,  # First positional argument
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

            logger.info("Found %d search results for: %s", len(results), query)
            return results

        except Exception as e:
            logger.error("DuckDuckGo search error: %s", e)
            return []
