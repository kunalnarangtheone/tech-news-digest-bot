#!/usr/bin/env python
"""Initialize Neo4j Aura database with schema, constraints, and indexes."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def init_neo4j():
    """Initialize Neo4j database with schema."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    if not all([uri, password]):
        print("❌ Error: NEO4J_URI and NEO4J_PASSWORD must be set")
        sys.exit(1)

    print("Initializing Neo4j Aura schema...")
    print(f"URI: {uri}")
    print(f"Database: {database}\n")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session(database=database) as session:
            # Create unique constraints
            print("Creating constraints...")

            try:
                session.run("""
                    CREATE CONSTRAINT article_url_unique IF NOT EXISTS
                    FOR (a:Article) REQUIRE a.url IS UNIQUE
                """)
                print("  ✓ article_url_unique constraint created")
            except Exception as e:
                print(f"  ⚠ article_url_unique constraint: {e}")

            try:
                session.run("""
                    CREATE CONSTRAINT topic_name_unique IF NOT EXISTS
                    FOR (t:Topic) REQUIRE t.name IS UNIQUE
                """)
                print("  ✓ topic_name_unique constraint created")
            except Exception as e:
                print(f"  ⚠ topic_name_unique constraint: {e}")

            # Create regular indexes
            print("\nCreating indexes...")

            try:
                session.run("""
                    CREATE INDEX article_timestamp IF NOT EXISTS
                    FOR (a:Article) ON (a.timestamp)
                """)
                print("  ✓ article_timestamp index created")
            except Exception as e:
                print(f"  ⚠ article_timestamp index: {e}")

            try:
                session.run("""
                    CREATE INDEX topic_name IF NOT EXISTS
                    FOR (t:Topic) ON (t.name)
                """)
                print("  ✓ topic_name index created")
            except Exception as e:
                print(f"  ⚠ topic_name index: {e}")

            # Create full-text indexes for BM25 search
            print("\nCreating full-text indexes (BM25)...")

            try:
                session.run("""
                    CREATE FULLTEXT INDEX article_fulltext IF NOT EXISTS
                    FOR (a:Article)
                    ON EACH [a.title, a.content, a.snippet]
                """)
                print("  ✓ article_fulltext index created (title, content, snippet)")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ℹ article_fulltext index already exists")
                else:
                    print(f"  ⚠ article_fulltext index: {e}")

            try:
                session.run("""
                    CREATE FULLTEXT INDEX topic_fulltext IF NOT EXISTS
                    FOR (t:Topic)
                    ON EACH [t.name, t.display_name]
                """)
                print("  ✓ topic_fulltext index created (name, display_name)")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ℹ topic_fulltext index already exists")
                else:
                    print(f"  ⚠ topic_fulltext index: {e}")

            # Create vector index for article embeddings
            print("\nCreating vector index...")

            try:
                session.run("""
                    CALL db.index.vector.createNodeIndex(
                        'article_embeddings',
                        'Article',
                        'embedding',
                        768,
                        'cosine'
                    )
                """)
                print("  ✓ article_embeddings vector index created (768 dimensions, cosine similarity)")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  ℹ article_embeddings vector index already exists")
                else:
                    print(f"  ⚠ article_embeddings vector index: {e}")

            # Verify indexes
            print("\nVerifying indexes...")
            result = session.run("SHOW INDEXES")
            indexes = list(result)

            print(f"\nTotal indexes: {len(indexes)}")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['type']} on {idx.get('labelsOrTypes', idx.get('entityType', 'N/A'))}")

            print("\n✅ Neo4j schema initialization complete!")

    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    init_neo4j()
