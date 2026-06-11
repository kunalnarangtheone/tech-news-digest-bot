"""Search agent node - parallelizable web search unit."""

import logging

from ...scraping import WebScrapingError, fetch_and_extract
from ...search import DuckDuckGoSearch

logger = logging.getLogger(__name__)


async def search_agent(state: dict) -> dict:
    """
    Individual search agent (invoked via Send() for parallel execution).

    This is THE KEY parallelizable unit - each instance searches one sub-question.

    Args:
        state: Contains 'sub_question' (str) - NOT the full GraphState
              This is a subset passed by Send() for parallelism

    Returns:
        Dict with 'search_results' key containing list of source dicts
    """
    sub_question = state["sub_question"]

    logger.info(f"Search agent starting: {sub_question[:80]}...")

    try:
        # Perform DuckDuckGo search
        ddg = DuckDuckGoSearch()
        results = await ddg.search(sub_question, max_results=5)

        if not results:
            logger.warning(f"No results for: {sub_question[:50]}...")
            return {"search_results": []}

        # Fetch full page content for top results
        enriched_results = []

        for _i, result in enumerate(results[:3]):  # Top 3 results
            try:
                # Try to fetch full page content
                content = await fetch_and_extract(
                    result["url"], max_chars=5000
                )

                enriched_results.append(
                    {
                        "url": result["url"],
                        "title": result["title"],
                        "content": content,  # Full page content
                        "sub_question": sub_question,
                    }
                )

                logger.info(
                    f"Fetched full content from {result['url'][:50]}..."
                )

            except WebScrapingError as e:
                # Fallback to DuckDuckGo snippet if scraping fails
                logger.warning(
                    f"Scraping failed for {result['url'][:50]}..., "
                    f"using snippet: {e}"
                )

                enriched_results.append(
                    {
                        "url": result["url"],
                        "title": result["title"],
                        "content": result[
                            "content"
                        ],  # DuckDuckGo snippet fallback
                        "sub_question": sub_question,
                    }
                )

        logger.info(
            f"Search agent completed: {len(enriched_results)} sources for "
            f"{sub_question[:50]}..."
        )

        return {"search_results": enriched_results}

    except Exception as e:
        logger.error(f"Search agent failed for '{sub_question[:50]}...': {e}")
        return {"search_results": []}
