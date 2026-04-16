"""Type definitions for the tech digest bot."""

from typing import TypedDict


class SearchResult(TypedDict):
    """Web search result."""

    title: str
    url: str
    content: str


class HackerNewsStory(TypedDict):
    """HackerNews story."""

    rank: int
    title: str
    url: str
    domain: str
    score: str
    age: str
    comments: str
    hn_url: str


class GitHubRepo(TypedDict):
    """GitHub repository."""

    rank: int
    name: str
    url: str
    description: str
    language: str
    stars: str
    stars_today: str
    forks: str
    contributors: int


class DevToArticle(TypedDict):
    """Dev.to article."""

    rank: int
    title: str
    url: str
    author: str
    tags: list[str]
    reactions: str
    comments: str
    read_time: str
    published_date: str
    snippet: str


class TechNews(TypedDict):
    """Aggregated tech news from multiple sources."""

    hackernews: list[HackerNewsStory]
    github: list[GitHubRepo]
    devto: list[DevToArticle]
    reddit: list[dict]
