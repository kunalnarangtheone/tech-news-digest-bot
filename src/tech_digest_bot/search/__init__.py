"""Search providers and clients."""

from .duckduckgo import DuckDuckGoSearch
from .openclaw_cli import OpenClawCLIClient

__all__ = ["DuckDuckGoSearch", "OpenClawCLIClient"]
