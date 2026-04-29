"""Web search tool with automatic ingestion to knowledge graph."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from langchain_core.documents import Document
from pydantic import Field

from .base import TechDigestBaseTool, ToolInput
from ...config.constants import MAX_SEARCH_RESULTS, SNIPPET_LENGTH
from ...exceptions import WebSearchError, IngestionError

if TYPE_CHECKING:
    from ...graph.neo4j_store import TechDigestNeo4jStore
    from ...config.settings import Settings

logger = logging.getLogger(__name__)


class WebSearchInput(ToolInput):
    """Input schema for web search."""

    pass


class WebSearchTool(TechDigestBaseTool):
    """Search web and automatically ingest to knowledge graph."""

    name: str = "search_web_and_ingest"
    description: str = """Search the web for current information and add to knowledge graph.

Performs DuckDuckGo search, extracts topics, creates graph
relationships, and returns formatted results. All results are
automatically saved to the knowledge graph for future queries.

Use this when:
- Looking for breaking news or recent developments
- Topic not found in knowledge graph
- User asks about current events or trends
- Need fresh, up-to-date information"""

    args_schema: type[ToolInput] = WebSearchInput

    # Dependencies
    neo4j_store: "TechDigestNeo4jStore" = Field(exclude=True)
    settings: "Settings" = Field(exclude=True)
    llm_client: Any = Field(exclude=True)

    async def _arun(self, query: str) -> str:
        """Execute web search and ingestion."""
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

            # Convert to documents
            documents, metadata = self._prepare_documents(results)

            # Ingest to Neo4j
            await self._ingest_documents(documents, metadata)

            # Format response
            return self._format_response(results, len(metadata))

        except Exception as e:
            logger.exception(f"Web search failed: {e}")
            raise WebSearchError(f"Web search and ingestion failed: {e}")

    def _prepare_documents(
        self, results: list[dict]
    ) -> tuple[list[Document], list[dict]]:
        """Convert search results to LangChain documents."""
        documents = []
        metadata = []

        for result in results:
            article_id = str(uuid.uuid4())

            doc = Document(
                page_content=result["content"],
                metadata={
                    "id": article_id,
                    "title": result["title"],
                    "url": result["url"],
                    "source": "DuckDuckGo",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "snippet": result["content"][:SNIPPET_LENGTH],
                },
            )
            documents.append(doc)
            metadata.append(
                {
                    "id": article_id,
                    "title": result["title"],
                    "content": result["content"],
                }
            )

        return documents, metadata

    async def _filter_existing_documents(
        self, documents: list[Document], metadata: list[dict]
    ) -> tuple[list[Document], list[dict]]:
        """Filter out documents with URLs that already exist in Neo4j."""
        # Extract all URLs
        urls = [doc.metadata["url"] for doc in documents]

        # Check which URLs already exist
        driver = self.neo4j_store.get_driver()
        async with driver.session(database=self.settings.neo4j_database) as session:
            result = await session.run(
                """
                UNWIND $urls AS url
                MATCH (a:Article {url: url})
                RETURN a.url AS url
                """,
                urls=urls,
            )
            existing_urls = {record["url"] async for record in result}

        # Filter to only new documents
        new_documents = []
        new_metadata = []
        skipped_count = 0

        for doc, meta in zip(documents, metadata):
            if doc.metadata["url"] not in existing_urls:
                new_documents.append(doc)
                new_metadata.append(meta)
            else:
                skipped_count += 1

        if skipped_count > 0:
            logger.info(f"Skipping {skipped_count} articles that already exist")

        return new_documents, new_metadata

    async def _ingest_documents(
        self, documents: list[Document], metadata: list[dict]
    ):
        """Ingest documents with topic extraction."""
        from ...graph.graph_queries import (
            create_topic_relationships,
            extract_topics_with_llm,
        )

        try:
            # Filter out documents with URLs that already exist
            new_docs, new_metadata = await self._filter_existing_documents(
                documents, metadata
            )

            if not new_docs:
                logger.info("All articles already exist in Neo4j, skipping ingestion")
                return

            # Add to Neo4j
            logger.info(f"Ingesting {len(new_docs)} new articles to Neo4j...")
            await self.neo4j_store.add_documents(new_docs)
            logger.info("✓ Articles ingested successfully")

            # Extract topics and create relationships
            driver = self.neo4j_store.get_driver()
            total_topics = 0

            for article_meta in new_metadata:
                topics = await extract_topics_with_llm(
                    article_meta["content"],
                    article_meta["title"],
                    self.llm_client,
                )
                if topics:
                    await create_topic_relationships(
                        driver,
                        article_meta["id"],
                        topics,
                        self.settings.neo4j_database,
                    )
                    total_topics += len(topics)

            logger.info(
                f"✓ Created relationships for {total_topics} topics via LLM"
            )

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise IngestionError(f"Failed to ingest documents: {e}")

    def _format_response(
        self, results: list[dict], topic_count: int
    ) -> str:
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

        summary = (
            f"Found {len(results)} articles and added to "
            f"knowledge graph ({topic_count} total topics):\n\n"
        )
        return summary + "\n".join(formatted)
