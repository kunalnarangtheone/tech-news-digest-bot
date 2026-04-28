# 🤖 Tech Digest Bot - Graph-RAG Intelligence Hub

An AI-powered Telegram bot with **persistent knowledge graph** capabilities powered by LangChain, Neo4j Aura, and Ollama.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Aura-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## ✨ Features

### 🧠 **Intelligent Agent with Tool Routing**
- **LangChain Agent** intelligently decides which tools to use
- **BM25 Full-Text Search** for keyword relevance (works on Neo4j Aura free tier)
- **Automatic Web Search + Ingestion** when topics not in knowledge graph
- **Graph Relationship Exploration** for discovering connected topics

### 📊 **Persistent Knowledge Graph**
- **Neo4j Aura** cloud database with graph relationships + BM25 search
- **Automatic Topic Extraction** from articles (70+ tech keywords)
- **Relationship Discovery** between co-occurring topics
- **Incremental Learning** - every search enriches the knowledge base

### 🔍 **Multi-Source Research**
- **Priority Chain:**
  1. 🥇 **LangChain Agent** (knowledge graph + BM25 + web search)
  2. 🥈 **DuckDuckGo + Ollama** (basic fallback)

### ⚡ **Performance**
- **Average Response Time:** 5-10 seconds
- **Knowledge Graph Queries:** < 1 second
- **Automatic Caching:** Previously searched topics return instantly
- **Weekly Backups:** GitHub Actions backup to repository

## 🚀 Quick Start

### Prerequisites

- **Python 3.14+**
- **Ollama** ([install](https://ollama.ai))
- **Neo4j Aura** account (free tier - [sign up](https://neo4j.com/cloud/aura/))
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/tech-news-digest-bot.git
cd tech-news-digest-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Pull Ollama Models

```bash
ollama pull qwen2.5:7b        # LLM for reasoning
ollama pull nomic-embed-text  # Embeddings (768-dim)
```

### Configuration

Create `.env` file:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_token_from_botfather

# Ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b

# LangChain Agent
USE_LANGCHAIN_AGENT=true

# Neo4j Aura (get from https://console.neo4j.io)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=your_aura_instance_id
NEO4J_PASSWORD=your_aura_password
NEO4J_DATABASE=neo4j

# Embeddings
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSION=768
```

### Initialize Neo4j

```bash
python scripts/init_neo4j.py
```

### Run Bot

```bash
# Start Ollama (if not running)
ollama serve

# Run bot
python -m tech_digest_bot.bot.app
```

## 📖 Usage

### Telegram Commands

```
/start  - Welcome message
/help   - Show help
/new    - Start new conversation
```

### Example Conversations

**Basic Query:**
```
User: What is Rust programming language?

Bot: [Comprehensive answer with]:
- Overview of Rust features
- Memory safety model
- Performance characteristics
- Use cases
- Source URLs (3-5 references)
```

**Follow-up Question:**
```
User: How does it compare to Python?

Bot: [Context-aware comparison]:
- Rust: Systems programming, memory safety, performance
- Python: High-level, ease of use, GC
- Trade-offs and use case recommendations
```

## 🧪 Testing

### Run All Tests

```bash
# Comprehensive end-to-end tests
python scripts/test_end_to_end.py
```

**Expected Results:**
```
Total Tests: 17
✅ Passed: 17
❌ Failed: 0
Success Rate: 100.0%
```

### Test Individual Components

```bash
# Neo4j connection
python scripts/test_neo4j_connection.py

# Graph queries + BM25
python scripts/test_hybrid_search.py

# LangChain tools
python scripts/test_langchain_tools.py

# Agent reasoning
python scripts/test_agent.py

# Bot integration
python scripts/test_bot_integration.py
```

## 📊 Knowledge Graph Schema

```cypher
// Article nodes
(:Article {
    id: STRING,
    url: STRING (unique),
    title: STRING,
    content: TEXT,
    snippet: STRING,
    timestamp: DATETIME
})

// Topic nodes
(:Topic {
    id: STRING,
    name: STRING (unique, lowercase),
    display_name: STRING,
    article_count: INT
})

// Relationships
(:Article)-[:DISCUSSES {relevance: FLOAT}]->(:Topic)
(:Topic)-[:RELATED_TO {weight: INT, strength: FLOAT}]->(:Topic)
```

## 🎯 Performance Benchmarks

| Metric | Value |
|--------|-------|
| **Average Response Time** | 8.5 seconds |
| **Knowledge Graph Search** | < 1 second |
| **Web Search + Ingestion** | 5-15 seconds |
| **Topic Exploration** | < 1 second |
| **Follow-up Questions** | 10-20 seconds |

## 📦 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker deployment
- systemd service (Linux)
- PM2 (Node.js process manager)
- Production configuration
- Monitoring and health checks

## 🔄 Automated Backups

Weekly backups via GitHub Actions (Sundays 2 AM UTC):

```bash
# Manual backup
python scripts/backup_neo4j.py

# Restore
python scripts/restore_neo4j.py backups/neo4j/backup_2026-04-28.cypher
```

## Project Structure

```
tech-news-digest-bot/
├── src/tech_digest_bot/
│   ├── ai/
│   │   ├── agent.py          # LangChain agent
│   │   ├── tools/            # Graph search, web search, explore
│   │   ├── llm.py            # Ollama LLM client
│   │   └── research.py       # Research service
│   ├── graph/
│   │   ├── neo4j_store.py    # Neo4j wrapper
│   │   └── graph_queries.py  # BM25 + Cypher queries
│   ├── bot/                  # Telegram bot
│   ├── search/               # DuckDuckGo
│   └── config/               # Settings
├── scripts/                  # Test and utility scripts
├── docs/                     # Documentation
└── backups/neo4j/            # Automated backups
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [BM25 Search](docs/BM25_SEARCH.md) - Search implementation
- [Implementation Plan](/.claude/plans/i-am-ready-to-unified-ripple.md) - Architecture

## 🧩 Key Technologies

- **[LangChain](https://python.langchain.com/)** - Agent framework
- **[Neo4j Aura](https://neo4j.com/cloud/aura/)** - Graph database
- **[Ollama](https://ollama.ai/)** - Local LLM inference
- **[Telegram Bot API](https://core.telegram.org/bots/api)** - Bot platform

## 🤝 Contributing

Contributions welcome! Ideas:
- Enhanced topic extraction with NER
- Query expansion for better search
- Multi-language support
- Scheduled RSS ingestion
- Graph analytics (PageRank, clustering)

## 📝 License

MIT

---

**Built with ❤️ using LangChain, Neo4j Aura, and Ollama**
