"""OpenClaw Gateway client for browser automation."""

import logging
from typing import Any, Optional

import aiohttp

from ..models import DevToArticle, GitHubRepo, HackerNewsStory, TechNews

logger = logging.getLogger(__name__)


class OpenClawClient:
    """Client for OpenClaw Gateway API."""

    def __init__(self, base_url: str = "http://localhost:3000") -> None:
        """
        Initialize OpenClaw client.

        Args:
            base_url: OpenClaw Gateway URL
        """
        self.base_url = base_url
        self.enabled = False

    async def check_availability(self) -> bool:
        """
        Check if OpenClaw Gateway is available.

        Returns:
            True if Gateway is reachable, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    self.enabled = response.status == 200
                    return self.enabled
        except Exception as e:
            logger.warning(f"OpenClaw Gateway not available: {e}")
            self.enabled = False
            return False

    async def execute_skill(
        self, skill_name: str, args: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Execute an OpenClaw JavaScript skill.

        Args:
            skill_name: Name of the skill to execute
            args: Arguments to pass to the skill

        Returns:
            Skill execution result with 'success' and 'data' or 'error' keys
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"skill": skill_name, "args": args or {}}

                async with session.post(
                    f"{self.base_url}/api/skills/execute",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Skill {skill_name} executed successfully")
                        return {"success": True, "data": result.get("data", result)}
                    else:
                        error_text = await response.text()
                        logger.error(f"Skill execution failed: {error_text}")
                        return {"success": False, "error": error_text}

        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {e}")
            return {"success": False, "error": str(e)}

    async def get_hackernews_top(self, limit: int = 10) -> list[HackerNewsStory]:
        """
        Get top HackerNews stories via OpenClaw browser automation.

        Args:
            limit: Maximum number of stories to retrieve

        Returns:
            List of HackerNews stories
        """
        result = await self.execute_skill("hackernews-top-stories", {"limit": limit})
        if result.get("success"):
            return result.get("data", [])
        return []

    async def get_github_trending(
        self, language: str = "", timeframe: str = "daily"
    ) -> list[GitHubRepo]:
        """
        Get GitHub trending repositories via OpenClaw browser automation.

        Args:
            language: Programming language filter (e.g., 'python', 'rust')
            timeframe: Time period ('daily', 'weekly', 'monthly')

        Returns:
            List of GitHub repositories
        """
        result = await self.execute_skill(
            "github-trending", {"language": language, "timeframe": timeframe}
        )
        if result.get("success"):
            return result.get("data", [])
        return []

    async def get_devto_trending(
        self, tag: str = "", timeframe: str = "week"
    ) -> list[DevToArticle]:
        """
        Get Dev.to trending articles via OpenClaw browser automation.

        Args:
            tag: Topic tag filter (e.g., 'python', 'webdev')
            timeframe: Time period ('day', 'week', 'month', 'year')

        Returns:
            List of Dev.to articles
        """
        result = await self.execute_skill(
            "devto-trending", {"tag": tag, "timeframe": timeframe}
        )
        if result.get("success"):
            return result.get("data", [])
        return []

    async def get_reddit_tech(
        self, subreddit: str = "programming", limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get top posts from tech subreddits via OpenClaw.

        Args:
            subreddit: Subreddit name
            limit: Maximum number of posts

        Returns:
            List of Reddit posts
        """
        result = await self.execute_skill(
            "reddit-scraper", {"subreddit": subreddit, "limit": limit}
        )
        if result.get("success"):
            return result.get("data", [])
        return []

    async def aggregate_tech_news(
        self, topic_filter: Optional[str] = None
    ) -> TechNews:
        """
        Aggregate news from multiple sources in parallel.

        Args:
            topic_filter: Optional keyword to filter results

        Returns:
            Aggregated tech news from all sources
        """
        import asyncio

        # Run all scrapers in parallel for speed
        results = await asyncio.gather(
            self.get_hackernews_top(limit=10),
            self.get_github_trending(timeframe="daily"),
            self.get_devto_trending(timeframe="day"),
            self.get_reddit_tech(limit=10),
            return_exceptions=True,
        )

        # Extract results, handling any exceptions
        aggregated = TechNews(
            hackernews=results[0] if not isinstance(results[0], Exception) else [],
            github=results[1] if not isinstance(results[1], Exception) else [],
            devto=results[2] if not isinstance(results[2], Exception) else [],
            reddit=results[3] if not isinstance(results[3], Exception) else [],
        )

        # Apply topic filter if provided
        if topic_filter:
            keywords = topic_filter.lower().split()

            aggregated["hackernews"] = [
                item
                for item in aggregated["hackernews"]
                if any(kw in item.get("title", "").lower() for kw in keywords)
            ]

            aggregated["github"] = [
                item
                for item in aggregated["github"]
                if any(
                    kw in item.get("name", "").lower()
                    or kw in item.get("description", "").lower()
                    for kw in keywords
                )
            ]

            aggregated["devto"] = [
                item
                for item in aggregated["devto"]
                if any(kw in item.get("title", "").lower() for kw in keywords)
            ]

            aggregated["reddit"] = [
                item
                for item in aggregated["reddit"]
                if any(kw in item.get("title", "").lower() for kw in keywords)
            ]

        return aggregated
