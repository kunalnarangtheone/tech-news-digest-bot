"""AI and research components."""

from .llm import LLMClient
from .research import ResearchService

# Lazy import to avoid requiring langchain dependencies
def __getattr__(name):
    if name == "TechIntelligenceAgent":
        from .agent import TechIntelligenceAgent
        return TechIntelligenceAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["LLMClient", "ResearchService", "TechIntelligenceAgent"]
