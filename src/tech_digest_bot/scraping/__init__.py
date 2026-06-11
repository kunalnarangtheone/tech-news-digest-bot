"""Web scraping utilities for full page content extraction."""

from .webpage import WebScrapingError, fetch_and_extract

__all__ = ["fetch_and_extract", "WebScrapingError"]
