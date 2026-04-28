"""LangChain Neo4j vector store wrapper for tech digest bot."""

import logging

from neo4j import AsyncGraphDatabase
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_ollama import OllamaEmbeddings

from ..exceptions import Neo4jConnectionError

logger = logging.getLogger(__name__)


class TechDigestNeo4jStore:
    """Wrapper around LangChain Neo4jVector for tech digest bot."""

    def __init__(self, settings):
        """
        Initialize Neo4j vector store with Ollama embeddings.

        Args:
            settings: Settings object with Neo4j and Ollama configuration
        """
        self.settings = settings

        # Initialize Ollama embeddings
        logger.info(
            f"Initializing Ollama embeddings with model: "
            f"{settings.embedding_model}"
        )

        # For Ollama, we need to use the base URL without /v1 suffix
        ollama_base = settings.ollama_base_url.replace("/v1", "")

        self.embeddings = OllamaEmbeddings(
            model=settings.embedding_model,  # nomic-embed-text
            base_url=ollama_base,
        )

        # Initialize Neo4j vector store
        logger.info(f"Connecting to Neo4j at {settings.neo4j_uri}")

        try:
            # Create async driver for custom Cypher queries
            self._async_driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )

            # Initialize LangChain vector store (uses its own driver internally)
            self.vector_store = Neo4jVector(
                url=settings.neo4j_uri,
                username=settings.neo4j_user,
                password=settings.neo4j_password,
                database=settings.neo4j_database,
                embedding=self.embeddings,
                index_name="article_embeddings",
                node_label="Article",
                text_node_property="content",
                embedding_node_property="embedding",
                # Custom retrieval query to get additional metadata
                retrieval_query="""
                RETURN node.content AS text, score,
                       {
                           title: node.title,
                           url: node.url,
                           source: node.source,
                           timestamp: node.timestamp,
                           snippet: node.snippet,
                           id: node.id
                       } AS metadata
                """,
            )

            logger.info("✓ Neo4j vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j vector store: {e}")
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}")

    async def similarity_search(
        self, query: str, k: int = 5
    ) -> list[tuple[Document, float]]:
        """
        Perform similarity search on knowledge graph.

        Args:
            query: Search query text
            k: Number of results to return (default: 5)

        Returns:
            List of (Document, score) tuples
        """
        try:
            results = await self.vector_store.asimilarity_search_with_score(
                query, k=k
            )
            logger.info(
                f"Found {len(results)} similar documents for "
                f"query: {query[:50]}..."
            )
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def bm25_search(self, query: str, k: int = 5) -> list[dict]:
        """
        Perform BM25 full-text search on articles.

        This works on Neo4j Aura free tier (no vector index required).

        Args:
            query: Search query text
            k: Number of results to return (default: 5)

        Returns:
            List of article dicts with BM25 scores
        """
        try:
            from .graph_queries import bm25_search_articles

            driver = self.get_driver()
            results = await bm25_search_articles(
                driver, query, self.settings.neo4j_database, limit=k
            )

            logger.info(
                f"BM25 search found {len(results)} results for "
                f"query: {query[:50]}..."
            )
            return results

        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []

    async def hybrid_search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5,
    ) -> list[dict]:
        """
        Perform hybrid search combining vector similarity and BM25.

        NOTE: Neo4j Aura free tier doesn't support vector indexes,
        so this will fall back to BM25-only search on Aura free.
        Hybrid search works on:
        - Neo4j Aura paid tiers
        - Self-hosted Neo4j 5.x+ with vector index support

        Uses Reciprocal Rank Fusion (RRF) to combine:
        - Vector similarity (semantic understanding)
        - BM25 full-text search (keyword relevance)

        Args:
            query: Search query text
            k: Number of results to return (default: 5)
            vector_weight: Weight for vector similarity
                (0.0-1.0, default: 0.5)
            bm25_weight: Weight for BM25 score (0.0-1.0, default: 0.5)

        Returns:
            List of article dicts with hybrid scores
        """
        try:
            from .graph_queries import hybrid_search_articles

            # Try vector similarity search
            vector_results = await self.vector_store.asimilarity_search_with_score(
                query, k=k * 2  # Get more for better fusion
            )

            # Perform hybrid search
            driver = self.get_driver()
            results = await hybrid_search_articles(
                driver,
                query,
                vector_results,
                self.settings.neo4j_database,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight,
                limit=k,
            )

            logger.info(
                f"Hybrid search found {len(results)} results for "
                f"query: {query[:50]}..."
            )
            return results

        except Exception as e:
            # Fallback to BM25-only (works on Aura free tier)
            logger.warning(
                f"Vector search not available (Aura free tier limitation), "
                f"using BM25-only search: {e}"
            )
            return await self.bm25_search(query, k=k)

    async def add_documents(self, documents: list[Document]) -> list[str]:
        """
        Add documents to vector store with embeddings.

        Args:
            documents: List of LangChain Document objects

        Returns:
            List of node IDs created
        """
        try:
            ids = await self.vector_store.aadd_documents(documents)
            logger.info(f"✓ Added {len(ids)} documents to Neo4j vector store")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def get_driver(self):
        """
        Get async Neo4j driver for custom Cypher queries.

        Use this for graph traversal and relationship queries.

        Returns:
            AsyncDriver instance for custom queries
        """
        return self._async_driver

    async def close(self):
        """Close async Neo4j driver connection."""
        if self._async_driver:
            await self._async_driver.close()
            logger.info("Neo4j async driver connection closed")
