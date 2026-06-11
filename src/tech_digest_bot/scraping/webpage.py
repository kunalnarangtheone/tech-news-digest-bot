"""Web page content extraction with httpx and BeautifulSoup."""

import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScrapingError(Exception):
    """Raised when web scraping fails."""

    pass


async def fetch_and_extract(
    url: str,
    max_chars: int = 5000,
    timeout: float = 10.0,
) -> str:
    """
    Fetch a URL and extract clean text content.

    Args:
        url: URL to fetch
        max_chars: Maximum characters to return (truncate longer content)
        timeout: Request timeout in seconds

    Returns:
        Cleaned text content from the page

    Raises:
        WebScrapingError: If fetching or parsing fails
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
        }

        async with httpx.AsyncClient(
            timeout=timeout, follow_redirects=True
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for element in soup(
                ["script", "style", "nav", "footer", "header", "aside"]
            ):
                element.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            # Clean up excessive newlines
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)

            # Truncate if needed
            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "..."

            logger.info(
                f"Extracted {len(clean_text)} chars from {url[:50]}..."
            )
            return clean_text

    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching {url}: {e.response.status_code}")
        raise WebScrapingError(
            f"HTTP {e.response.status_code} for {url}"
        ) from e

    except httpx.TimeoutException as e:
        logger.warning(f"Timeout fetching {url}")
        raise WebScrapingError(f"Timeout fetching {url}") from e

    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        raise WebScrapingError(f"Failed to extract from {url}: {e}") from e
