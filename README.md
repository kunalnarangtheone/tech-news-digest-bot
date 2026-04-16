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
- [OpenRouter API key](https://openrouter.ai/) (free tier available)
- (Optional) Node.js 18+ for OpenClaw integration

### Installation

```bash
# Clone repository
git clone <repo-url>
cd openclaw-bot

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
OPENROUTER_API_KEY=your_api_key
```

### Run the Bot

```bash
# Run directly
python -m tech_digest_bot

# Or use the installed script
tech-digest-bot
```

## OpenClaw Integration (Optional)

For advanced research with browser automation:

```bash
# 1. Install OpenClaw
npm install -g openclaw
openclaw start

# 2. Install skills
cp openclaw/skills/*.js ~/.openclaw/skills/

# 3. Enable in .env
OPENCLAW_ENABLED=true

# 4. Test integration
python scripts/test_integration.py
```

See [docs/openclaw-integration.md](docs/openclaw-integration.md) for details.

## Project Structure

```
openclaw-bot/
├── src/tech_digest_bot/     # Main package
│   ├── bot/                  # Telegram bot logic
│   ├── ai/                   # LLM and research
│   ├── search/               # Search providers (DDG, OpenClaw)
│   ├── config/               # Configuration
│   └── models/               # Type definitions
├── openclaw/                 # OpenClaw resources
│   ├── skills/               # JavaScript browser automation
│   └── workflows/            # JavaScript cron workflows
├── tests/                    # Test suite
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
ruff format src/
```

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [OpenClaw Integration](docs/openclaw-integration.md)
- [Architecture](docs/architecture.md)

## License

MIT
