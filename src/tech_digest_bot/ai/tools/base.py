"""Base classes for LangChain tools."""

from abc import ABC, abstractmethod

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Base input schema for tools."""

    query: str = Field(description="Search query or topic")


class TechDigestBaseTool(BaseTool, ABC):
    """Base class for Tech Digest tools with dependency injection support."""

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    @abstractmethod
    async def _arun(self, query: str) -> str:
        """
        Execute tool logic (async).

        Args:
            query: Search query or topic

        Returns:
            Formatted result string
        """
        pass

    def _run(self, query: str) -> str:
        """
        Sync version (not supported).

        Raises:
            NotImplementedError: Always - use async _arun instead
        """
        raise NotImplementedError("Use async version _arun")
