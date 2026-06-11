"""Web search tool for finding current information."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from pydantic import Field

from ...config.constants import MAX_SEARCH_RESULTS
from ...exceptions import WebSearchError
from .base import TechDigestBaseTool, ToolInput

if TYPE_CHECKING:
    from ...config.settings import Settings

logger = logging.getLogger(__name__)


class WebSearchInput(ToolInput):
    """Input schema for web search."""

    pass


class WebSearchTool(TechDigestBaseTool):
    """Search web for current information."""

    name: str = "search_web"
    description: str = """Search the web for current information.

Performs DuckDuckGo search and returns formatted results.

Use this when:
- Looking for breaking news or recent developments
- User asks about current events or trends
- Need fresh, up-to-date information"""

    args_schema: type[ToolInput] = WebSearchInput

    # Dependencies
    settings: Settings = Field(exclude=True)
    llm_client: Any = Field(exclude=True)

    async def _arun(self, query: str) -> str:
        """Execute web search."""
        from ...search import DuckDuckGoSearch

        try:
            # Search
            logger.info(f"Searching web for: {query}")
            ddg = DuckDuckGoSearch()
            results = await ddg.search(query, max_results=MAX_SEARCH_RESULTS)

            if not results:
                return (
                    "No web results found. The topic might be too niche or "
                    "try rephrasing the query."
                )

            # Format response
            return self._format_response(results)

        except Exception as e:
            logger.exception(f"Web search failed: {e}")
            raise WebSearchError(f"Web search failed: {e}") from e

    def _format_response(self, results: list[dict]) -> str:
        """Format search results."""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"""
**{i}. {result['title']}**
URL: {result['url']}
Content: {result['content'][:250]}...
"""
            )

        summary = f"Found {len(results)} articles:\n\n"
        return summary + "\n".join(formatted)
