"""Custom Cypher queries for graph operations."""

import logging

logger = logging.getLogger(__name__)


# BM25 and Hybrid Search Functions


async def bm25_search_articles(
    driver, query: str, database: str, limit: int = 5
) -> list[dict]:
    """
    Perform BM25 full-text search on articles.

    Uses Neo4j's full-text index for keyword-based relevance scoring.

    Args:
        driver: AsyncDriver instance
        query: Search query text
        database: Neo4j database name
        limit: Maximum number of results

    Returns:
        List of articles with BM25 scores
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            CALL db.index.fulltext.queryNodes('article_fulltext', $search_query)
            YIELD node, score
            RETURN node.id as id,
                   node.title as title,
                   node.url as url,
                   node.content as content,
                   node.snippet as snippet,
                   node.timestamp as timestamp,
                   score as bm25_score
            ORDER BY score DESC
            LIMIT $limit
            """,
            search_query=query,
            limit=limit,
        )
        records = await result.data()
        return records


async def hybrid_search_articles(
    driver,
    query: str,
    vector_results: list[tuple],
    database: str,
    vector_weight: float = 0.5,
    bm25_weight: float = 0.5,
    limit: int = 5,
) -> list[dict]:
    """
    Hybrid search combining vector similarity and BM25 scores.

    Uses Reciprocal Rank Fusion (RRF) to combine rankings from
    both vector similarity and BM25 keyword search.

    Args:
        driver: Neo4j driver instance
        query: Search query text
        vector_results: Results from vector similarity search [(doc, score), ...]
        database: Neo4j database name
        vector_weight: Weight for vector similarity (default 0.5)
        bm25_weight: Weight for BM25 score (default 0.5)
        limit: Maximum number of results

    Returns:
        List of articles with combined hybrid scores
    """
    # Get BM25 results
    bm25_results = await bm25_search_articles(driver, query, database, limit=limit * 2)

    # Build article lookup from vector results
    vector_articles = {}
    for i, (doc, score) in enumerate(vector_results):
        article_id = doc.metadata.get("id")
        if article_id:
            vector_articles[article_id] = {
                "doc": doc,
                "vector_score": float(score),
                "vector_rank": i + 1,
            }

    # Build article lookup from BM25 results
    bm25_articles = {}
    for i, result in enumerate(bm25_results):
        article_id = result["id"]
        bm25_articles[article_id] = {
            "bm25_score": float(result["bm25_score"]),
            "bm25_rank": i + 1,
            "title": result["title"],
            "url": result["url"],
            "content": result["content"],
            "snippet": result["snippet"],
            "timestamp": result["timestamp"],
        }

    # Combine using Reciprocal Rank Fusion (RRF)
    all_article_ids = set(vector_articles.keys()) | set(bm25_articles.keys())

    combined_results = []
    for article_id in all_article_ids:
        vector_data = vector_articles.get(article_id, {})
        bm25_data = bm25_articles.get(article_id, {})

        # RRF formula: score = sum(1 / (k + rank))
        # k is typically 60 (constant from original RRF paper)
        k = 60

        vector_rank = vector_data.get("vector_rank", 999999)
        bm25_rank = bm25_data.get("bm25_rank", 999999)

        rrf_score = (vector_weight / (k + vector_rank)) + (
            bm25_weight / (k + bm25_rank)
        )

        # Get article data (prefer vector result for doc object)
        combined_results.append(
            {
                "id": article_id,
                "title": bm25_data.get("title")
                or vector_data.get("doc", {}).metadata.get("title"),
                "url": bm25_data.get("url")
                or vector_data.get("doc", {}).metadata.get("url"),
                "content": bm25_data.get("content")
                or vector_data.get("doc", {}).page_content,
                "snippet": bm25_data.get("snippet")
                or vector_data.get("doc", {}).metadata.get("snippet"),
                "timestamp": bm25_data.get("timestamp")
                or vector_data.get("doc", {}).metadata.get("timestamp"),
                "vector_score": vector_data.get("vector_score", 0.0),
                "bm25_score": bm25_data.get("bm25_score", 0.0),
                "hybrid_score": rrf_score,
            }
        )

    # Sort by hybrid score
    combined_results.sort(key=lambda x: x["hybrid_score"], reverse=True)

    return combined_results[:limit]


async def get_related_topics(driver, article_id: str, database: str) -> list[str]:
    """
    Get topics discussed in an article.

    Args:
        driver: AsyncDriver instance
        article_id: Article node ID
        database: Neo4j database name

    Returns:
        List of topic names
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            MATCH (a:Article {id: $article_id})-[:DISCUSSES]->(t:Topic)
            RETURN t.name as topic
            ORDER BY topic
            """,
            article_id=article_id,
        )
        records = await result.data()
        return [r["topic"] for r in records]


async def get_related_articles(
    driver, topic: str, database: str, limit: int = 5
) -> list[dict]:
    """
    Get articles discussing a specific topic.

    Args:
        driver: AsyncDriver instance
        topic: Topic name (normalized lowercase)
        database: Neo4j database name
        limit: Maximum number of articles to return

    Returns:
        List of article dictionaries with id, title, url, snippet
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            MATCH (t:Topic {name: $topic})<-[:DISCUSSES]-(a:Article)
            RETURN a.id as id, a.title as title, a.url as url,
                   a.snippet as snippet, a.timestamp as timestamp
            ORDER BY a.timestamp DESC
            LIMIT $limit
            """,
            topic=topic.lower(),
            limit=limit,
        )
        records = await result.data()
        return records


async def create_topic_relationships(
    driver, article_id: str, topics: list[str], database: str
):
    """
    Create DISCUSSES relationships between article and topics.

    Also creates RELATED_TO relationships between co-occurring topics.

    Args:
        driver: AsyncDriver instance
        article_id: Article node ID
        topics: List of topic names
        database: Neo4j database name
    """
    async with driver.session(database=database) as session:
        # Create topics and DISCUSSES relationships
        for topic in topics:
            await session.run(
                """
                MERGE (t:Topic {name: $topic_name})
                ON CREATE SET
                    t.id = randomUUID(),
                    t.display_name = $display_name,
                    t.article_count = 1,
                    t.created_at = datetime()
                ON MATCH SET
                    t.article_count = t.article_count + 1

                WITH t
                MATCH (a:Article {id: $article_id})
                MERGE (a)-[d:DISCUSSES]->(t)
                ON CREATE SET d.relevance = 1.0
                """,
                article_id=article_id,
                topic_name=topic.lower(),
                display_name=topic,
            )

        # Create RELATED_TO relationships between co-occurring topics
        if len(topics) > 1:
            for i, topic1 in enumerate(topics):
                for topic2 in topics[i + 1 :]:
                    await session.run(
                        """
                        MATCH (t1:Topic {name: $topic1}),
                              (t2:Topic {name: $topic2})
                        MERGE (t1)-[r:RELATED_TO]-(t2)
                        ON CREATE SET
                            r.weight = 1,
                            r.strength = 0.5
                        ON MATCH SET
                            r.weight = r.weight + 1,
                            r.strength = r.weight * 0.1
                        """,
                        topic1=topic1.lower(),
                        topic2=topic2.lower(),
                    )

        logger.info(
            f"Created relationships for article {article_id} "
            f"with {len(topics)} topics"
        )


async def find_related_topics(
    driver, topic: str, database: str, limit: int = 10
) -> list[dict]:
    """
    Find topics related to a given topic via RELATED_TO relationships.

    Args:
        driver: AsyncDriver instance
        topic: Topic name (normalized lowercase)
        database: Neo4j database name
        limit: Maximum number of related topics

    Returns:
        List of dicts with 'name' and 'strength' keys
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            MATCH (t:Topic {name: $topic})-[r:RELATED_TO]-(related:Topic)
            RETURN related.display_name as name, r.strength as strength
            ORDER BY r.strength DESC
            LIMIT $limit
            """,
            topic=topic.lower(),
            limit=limit,
        )
        records = await result.data()
        return records


async def get_topic_popularity(
    driver, topic: str, database: str
) -> dict:
    """
    Get popularity metrics for a topic.

    Args:
        driver: AsyncDriver instance
        topic: Topic name (normalized lowercase)
        database: Neo4j database name

    Returns:
        Dict with 'article_count' and 'created_at' keys
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            MATCH (t:Topic {name: $topic})
            RETURN t.article_count as article_count,
                   t.created_at as created_at
            """,
            topic=topic.lower(),
        )
        record = await result.single()
        return dict(record) if record else {}


async def get_recent_articles_on_topic(
    driver, topic: str, database: str, limit: int = 5
) -> list[dict]:
    """
    Get recent articles discussing a topic.

    Args:
        driver: AsyncDriver instance
        topic: Topic name (normalized lowercase)
        database: Neo4j database name
        limit: Maximum number of articles

    Returns:
        List of dicts with 'title', 'url', 'timestamp' keys
    """
    async with driver.session(database=database) as session:
        result = await session.run(
            """
            MATCH (t:Topic {name: $topic})<-[:DISCUSSES]-(a:Article)
            RETURN a.title as title,
                   a.url as url,
                   a.timestamp as timestamp
            ORDER BY a.timestamp DESC
            LIMIT $limit
            """,
            topic=topic.lower(),
            limit=limit,
        )
        records = await result.data()
        return records


async def extract_topics_with_llm(
    text: str, title: str, llm_client
) -> list[str]:
    """
    Extract topics/keywords from article text using LLM.

    Uses the LLM to dynamically identify key technical topics and concepts,
    which allows the system to work with any technical topic (not just
    a hardcoded keyword list).

    Args:
        text: Article content
        title: Article title
        llm_client: LLM client instance (from tech_digest_bot.ai.llm)

    Returns:
        List of extracted topic keywords (lowercase, normalized)
    """
    # Truncate content to avoid token limits
    content_preview = text[:1500] if len(text) > 1500 else text

    prompt = f"""Extract 5-10 key technical topics, concepts, or technologies from this article.

Title: {title}

Content: {content_preview}

Return ONLY a comma-separated list of topics in lowercase (no extra text, no explanations).
Focus on: programming languages, frameworks, tools, technologies, platforms, concepts.

Examples of good topics:
- Specific technologies: "python", "docker", "kubernetes", "react", "postgresql"
- Concepts: "microservices", "machine learning", "web development", "devops"
- Platforms: "aws", "github", "vercel", "netlify"

Topics (comma-separated):"""

    try:
        # Generate topics using LLM
        response = await llm_client.generate(prompt)

        # Parse comma-separated topics
        topics = [
            topic.strip().lower()
            for topic in response.strip().split(",")
            if topic.strip()
        ]

        # Clean up topics (remove quotes, extra whitespace)
        topics = [
            topic.replace('"', "").replace("'", "").strip()
            for topic in topics
        ]

        # Filter out empty strings and limit to 10
        topics = [t for t in topics if t and len(t) > 1][:10]

        logger.info(
            f"Extracted {len(topics)} topics via LLM: {', '.join(topics[:5])}..."
        )

        return topics

    except Exception as e:
        logger.error(f"LLM topic extraction failed: {e}")
        # Fallback to empty list
        return []
