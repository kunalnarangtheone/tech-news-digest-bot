#!/usr/bin/env python
"""
Backup Neo4j Aura database to Cypher file.
Run weekly via GitHub Actions or manually.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jBackup:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

        if not all([self.uri, self.password]):
            raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def export_to_cypher(self, output_dir: Path):
        """Export all nodes and relationships as Cypher statements."""

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")

        cypher_file = output_dir / f"backup_{timestamp}.cypher"
        metadata_file = output_dir / f"backup_{timestamp}_metadata.json"

        with self.driver.session(database=self.database) as session:
            # Get statistics
            stats = self._get_statistics(session)

            # Export nodes and relationships
            with open(cypher_file, "w", encoding="utf-8") as f:
                f.write(f"// Neo4j Backup - {timestamp}\n")
                f.write(
                    f"// Stats: {stats['node_count']} nodes, {stats['rel_count']} relationships\n\n"
                )

                # Export constraints and indexes
                f.write("// === Constraints ===\n")
                constraints = self._export_constraints(session)
                f.write(constraints + "\n\n")

                f.write("// === Indexes ===\n")
                indexes = self._export_indexes(session)
                f.write(indexes + "\n\n")

                # Export Article nodes
                if stats["article_count"] > 0:
                    f.write("// === Article Nodes ===\n")
                    articles = self._export_articles(session)
                    f.write(articles + "\n\n")

                # Export Topic nodes
                if stats["topic_count"] > 0:
                    f.write("// === Topic Nodes ===\n")
                    topics = self._export_topics(session)
                    f.write(topics + "\n\n")

                # Export relationships
                if stats["rel_count"] > 0:
                    f.write("// === DISCUSSES Relationships ===\n")
                    discusses = self._export_discusses_relationships(session)
                    f.write(discusses + "\n\n")

                    f.write("// === RELATED_TO Relationships ===\n")
                    related = self._export_related_to_relationships(session)
                    f.write(related + "\n\n")

            # Save metadata
            metadata = {
                "backup_date": timestamp,
                "database": self.database,
                "statistics": stats,
                "cypher_file": str(cypher_file.name),
            }

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        print(f"✓ Backup saved to {cypher_file}")
        print(f"  - {stats['node_count']} nodes")
        print(f"  - {stats['rel_count']} relationships")

        return cypher_file

    def _get_statistics(self, session) -> dict:
        """Get database statistics."""
        result = session.run("MATCH (n) RETURN count(n) as node_count")
        node_count = result.single()["node_count"]

        result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
        rel_count = result.single()["rel_count"]

        result = session.run("MATCH (a:Article) RETURN count(a) as count")
        article_count = result.single()["count"]

        result = session.run("MATCH (t:Topic) RETURN count(t) as count")
        topic_count = result.single()["count"]

        return {
            "node_count": node_count,
            "rel_count": rel_count,
            "article_count": article_count,
            "topic_count": topic_count,
        }

    def _export_constraints(self, session) -> str:
        """Export constraint definitions."""
        result = session.run("SHOW CONSTRAINTS")
        constraints = []

        for record in result:
            # Generate CREATE CONSTRAINT statement
            constraint_name = record.get("name", "")
            if "article_url_unique" in constraint_name:
                constraints.append(
                    "CREATE CONSTRAINT article_url_unique IF NOT EXISTS "
                    "FOR (a:Article) REQUIRE a.url IS UNIQUE;"
                )
            elif "topic_name_unique" in constraint_name:
                constraints.append(
                    "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS "
                    "FOR (t:Topic) REQUIRE t.name IS UNIQUE;"
                )

        return "\n".join(constraints) if constraints else "// No constraints"

    def _export_indexes(self, session) -> str:
        """Export index definitions."""
        indexes = []

        result = session.run("SHOW INDEXES")

        for record in result:
            index_name = record.get("name", "")

            if "article_timestamp" in index_name:
                indexes.append(
                    "CREATE INDEX article_timestamp IF NOT EXISTS "
                    "FOR (a:Article) ON (a.timestamp);"
                )
            elif "topic_name" in index_name and "unique" not in index_name.lower():
                indexes.append("CREATE INDEX topic_name IF NOT EXISTS " "FOR (t:Topic) ON (t.name);")

        # Note about vector index
        indexes.append(
            "\n// Vector index - LangChain Neo4jVector will create this automatically\n"
            "// No manual creation needed"
        )

        return "\n".join(indexes) if indexes else "// No indexes"

    def _export_articles(self, session) -> str:
        """Export all Article nodes."""
        result = session.run(
            """
            MATCH (a:Article)
            RETURN a
            ORDER BY a.timestamp
        """
        )

        statements = []
        for record in result:
            article = record["a"]
            props = dict(article.items())

            # Handle embedding separately (too large for inline, will be regenerated)
            props.pop("embedding", None)

            # Build MERGE statement
            url = props.get("url", "").replace("'", "\\'")
            article_id = props.get("id", "")

            stmt = f"MERGE (a:Article {{id: '{article_id}', url: '{url}'}}) SET "

            set_clauses = []
            for key, value in props.items():
                if key not in ["id", "url"]:
                    if isinstance(value, str):
                        value = value.replace("'", "\\'").replace("\n", "\\n")
                        set_clauses.append(f"a.{key} = '{value}'")
                    elif value is not None:
                        set_clauses.append(f"a.{key} = {value}")

            stmt += ", ".join(set_clauses)
            stmt += ";"
            statements.append(stmt)

        return "\n".join(statements) if statements else "// No articles"

    def _export_topics(self, session) -> str:
        """Export all Topic nodes."""
        result = session.run(
            """
            MATCH (t:Topic)
            RETURN t
            ORDER BY t.name
        """
        )

        statements = []
        for record in result:
            topic = record["t"]
            props = dict(topic.items())

            name = props.get("name", "").replace("'", "\\'")
            stmt = f"MERGE (t:Topic {{name: '{name}'}}) SET "

            set_clauses = []
            for key, value in props.items():
                if key != "name":
                    if isinstance(value, str):
                        value = value.replace("'", "\\'")
                        set_clauses.append(f"t.{key} = '{value}'")
                    elif value is not None:
                        set_clauses.append(f"t.{key} = {value}")

            stmt += ", ".join(set_clauses)
            stmt += ";"
            statements.append(stmt)

        return "\n".join(statements) if statements else "// No topics"

    def _export_discusses_relationships(self, session) -> str:
        """Export DISCUSSES relationships."""
        result = session.run(
            """
            MATCH (a:Article)-[d:DISCUSSES]->(t:Topic)
            RETURN a.id as article_id, t.name as topic_name, d.relevance as relevance
        """
        )

        statements = []
        for record in result:
            article_id = record["article_id"]
            topic_name = record["topic_name"].replace("'", "\\'")
            relevance = record.get("relevance", 1.0)

            stmt = (
                f"MATCH (a:Article {{id: '{article_id}'}}), "
                f"(t:Topic {{name: '{topic_name}'}}) "
                f"MERGE (a)-[d:DISCUSSES]->(t) "
                f"SET d.relevance = {relevance};"
            )
            statements.append(stmt)

        return "\n".join(statements) if statements else "// No DISCUSSES relationships"

    def _export_related_to_relationships(self, session) -> str:
        """Export RELATED_TO relationships."""
        result = session.run(
            """
            MATCH (t1:Topic)-[r:RELATED_TO]->(t2:Topic)
            WHERE id(t1) < id(t2)
            RETURN t1.name as topic1, t2.name as topic2, r.weight as weight, r.strength as strength
        """
        )

        statements = []
        for record in result:
            topic1 = record["topic1"].replace("'", "\\'")
            topic2 = record["topic2"].replace("'", "\\'")
            weight = record.get("weight", 1)
            strength = record.get("strength", 0.5)

            stmt = (
                f"MATCH (t1:Topic {{name: '{topic1}'}}), "
                f"(t2:Topic {{name: '{topic2}'}}) "
                f"MERGE (t1)-[r:RELATED_TO]-(t2) "
                f"SET r.weight = {weight}, r.strength = {strength};"
            )
            statements.append(stmt)

        return "\n".join(statements) if statements else "// No RELATED_TO relationships"

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    backup_dir = Path("backups/neo4j")

    print("Starting Neo4j backup...")
    backup = Neo4jBackup()

    try:
        backup.export_to_cypher(backup_dir)
        print("✓ Backup completed successfully")
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        raise
    finally:
        backup.close()
