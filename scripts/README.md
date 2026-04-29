# Scripts Directory - Migration Status

This directory contains legacy test and utility scripts written before the pytest framework was implemented.

## Status

**🔄 Migration Completed:** The refactoring introduced a proper pytest structure in `tests/`. Most test functionality has been migrated.

## File Classification

### Utility Scripts (Keep)
These scripts provide operational functionality not covered by pytest:

- **`backup_neo4j.py`** - Database backup utility
- **`init_neo4j.py`** - Neo4j initialization and schema setup
- **`restore_neo4j.py`** - Database restore utility

### Legacy Test Scripts (Deprecated)
These were standalone test scripts now replaced by pytest:

- ~~`test_agent.py`~~ → Use `pytest tests/integration/test_agent.py` (when created)
- ~~`test_bot_integration.py`~~ → Use `pytest tests/integration/`
- ~~`test_end_to_end.py`~~ → Use `pytest tests/e2e/`
- ~~`test_graph_queries.py`~~ → Use `pytest tests/integration/test_neo4j_store.py`
- ~~`test_hybrid_search.py`~~ → Use `pytest tests/integration/test_neo4j_store.py`
- ~~`test_langchain_tools.py`~~ → Use `pytest tests/integration/test_tools.py` (when created)
- ~~`test_llm_integration.py`~~ → Use `pytest tests/integration/test_llm.py` (when created)
- ~~`test_llm_topic_extraction.py`~~ → Use `pytest tests/unit/test_llm.py` (when created)
- ~~`test_neo4j_connection.py`~~ → Use `pytest tests/integration/test_neo4j_store.py`
- ~~`test_neo4j_store.py`~~ → Use `pytest tests/integration/test_neo4j_store.py`
- ~~`test_relevance_filtering.py`~~ → Use `pytest tests/unit/test_tools.py` (when created)

## Recommended Actions

### Option 1: Archive (Recommended)
```bash
mkdir -p scripts/archive
mv scripts/test_*.py scripts/archive/
```

### Option 2: Delete
If you're confident the new pytest structure covers everything:
```bash
rm scripts/test_*.py
```

### Option 3: Keep Temporarily
Keep them as reference until all integration/e2e tests are written in pytest, then delete.

## Running Tests Going Forward

### Unit Tests (Fast, No External Dependencies)
```bash
uv run pytest tests/unit/ -v
```

### Integration Tests (Requires Neo4j, Groq API Key)
```bash
uv run pytest tests/integration/ -v
```

### End-to-End Tests (Full System)
```bash
uv run pytest tests/e2e/ -v
```

### All Tests with Coverage
```bash
uv run pytest tests/ -v --cov=tech_digest_bot --cov-report=html
```

## Utility Scripts Usage

### Backup Neo4j Database
```bash
python scripts/backup_neo4j.py
```

### Initialize Neo4j (First Time Setup)
```bash
python scripts/init_neo4j.py
```

### Restore Neo4j from Backup
```bash
python scripts/restore_neo4j.py backups/neo4j/<backup_name>
```
