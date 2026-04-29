#!/usr/bin/env python
"""
Restore Neo4j database from backup Cypher file.
WARNING: This will clear existing data!
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def restore_from_backup(backup_file: Path):
    """Restore Neo4j from Cypher backup file."""

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)

    print(f"Restoring from: {backup_file}")
    print(f"Target database: {uri}")

    # Confirmation
    confirm = input("\n⚠️  This will DELETE all existing data. Continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Restore cancelled")
        sys.exit(0)

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session(database=database) as session:
            # Clear existing data
            print("\nClearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")

            # Read and execute Cypher statements
            print("\nRestoring from backup...")
            with open(backup_file, encoding="utf-8") as f:
                cypher_content = f.read()

            # Split by semicolon and execute each statement
            statements = [
                s.strip()
                for s in cypher_content.split(";")
                if s.strip() and not s.strip().startswith("//")
            ]

            total = len(statements)
            executed = 0

            for i, statement in enumerate(statements, 1):
                try:
                    if statement.strip():
                        session.run(statement)
                        executed += 1
                        if i % 100 == 0:
                            print(f"  Progress: {i}/{total} statements")
                except Exception as e:
                    print(f"  Warning: Failed to execute statement {i}: {e}")

            print(f"✓ Executed {executed}/{total} statements")

            # Get final count
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]

            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]

            print("\n✓ Restore complete!")
            print(f"  - {node_count} nodes")
            print(f"  - {rel_count} relationships")

            print(
                "\n⚠️  IMPORTANT: Embeddings were not backed up. "
                "They will be regenerated automatically when you use the bot."
            )

    finally:
        driver.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/restore_neo4j.py backups/neo4j/backup_2026-04-28.cypher")
        sys.exit(1)

    backup_file = Path(sys.argv[1])
    restore_from_backup(backup_file)
