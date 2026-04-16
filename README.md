# Tech Digest Bot 🤖

An AI-powered Telegram bot that researches tech topics and generates concise, digestible 2-minute summaries with optional OpenClaw integration for advanced browser automation.

## Features

- **🔍 Multi-Source Research**: DuckDuckGo search + optional OpenClaw browser automation
- **🧠 AI-Generated Digests**: Concise 2-minute summaries powered by LLMs
- **💬 Conversational**: Follow-up questions with context retention  
- **📱 Telegram Interface**: Works on all devices
- **🤖 OpenClaw Integration**: HackerNews, GitHub trending, Dev.to scraping
- **⚡ Modern Python**: Type hints, clean architecture, modular design

## Quick Start

### Prerequisites

- Python 3.14+
- Telegram account
- [Ollama](https://ollama.ai/) running locally
- (Optional) OpenClaw for enhanced research

### Installation

```bash
# Clone repository
git clone <repo-url>
cd tech-news-digest-bot

# Install dependencies
pip install -e .

# Or with uv (recommended)
uv sync
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add required values
TELEGRAM_BOT_TOKEN=your_bot_token

# Start Ollama (if not already running)
ollama serve
# Pull a model (e.g., qwen2.5:7b)
ollama pull qwen2.5:7b
```

### Run the Bot

```bash
# Run directly
python -m tech_digest_bot

# Or use the installed script
tech-digest-bot
```

## OpenClaw Integration (Optional)

For enhanced AI-powered research using OpenClaw CLI:

```bash
# 1. Start OpenClaw gateway
openclaw start

# 2. Enable in .env
OPENCLAW_ENABLED=true

# 3. Restart the bot
python -m tech_digest_bot
```

When enabled, the bot uses OpenClaw's AI agent for enhanced research capabilities.

## Project Structure

```
tech-news-digest-bot/
├── src/tech_digest_bot/     # Main package
│   ├── bot/                  # Telegram bot logic
│   ├── ai/                   # LLM and research
│   ├── search/               # Search providers (DDG, OpenClaw)
│   └── config/               # Configuration
├── docs/                     # Documentation
├── Makefile                  # Common tasks
└── run_bot.sh                # Bot launcher script
```

## Development

```bash
# Type checking
make typecheck

# Linting
make lint

# Formatting
make format

# Clean generated files
make clean
```

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [Architecture](docs/architecture.md)

## License

MIT
