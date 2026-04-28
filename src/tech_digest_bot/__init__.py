"""Tech Digest Bot - AI-powered tech research bot.

This module provides the main bot implementation.
"""

__version__ = "0.4.0"

from . import ai, bot, config, graph, search
from .bot import TechDigestBot

__all__ = [
    "__version__",
    "ai",
    "bot",
    "config",
    "graph",
    "search",
    "TechDigestBot",
]
