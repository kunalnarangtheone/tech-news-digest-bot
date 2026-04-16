# Quick Start Guide

Get your Tech Digest Bot running in 10 minutes.

## Basic Setup (Without OpenClaw)

### 1. Install Dependencies

```bash
pip install -e .

# Or with uv (recommended)
uv sync
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials:
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENROUTER_API_KEY=your_openrouter_api_key
OPENCLAW_ENABLED=false
```

Get tokens:
- **Telegram Bot Token**: Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot`
- **OpenRouter API Key**: Sign up at [openrouter.ai](https://openrouter.ai/)

### 3. Run the Bot

```bash
tech-digest-bot
```

You should see:
```
🤖 Starting Tech Digest Bot...
Model: google/gemini-2.0-flash-exp:free
OpenClaw enabled: False
Press Ctrl+C to stop
```

### 4. Test It

1. Open Telegram and find your bot
2. Send `/start`
3. Send a query: `Explain WebAssembly`
4. Get a 2-minute digest with web search results!

## Advanced Setup (With OpenClaw)

### Prerequisites

- Node.js 18+ installed
- Basic setup completed above

### 1. Run Setup Script

```bash
./scripts/setup_openclaw.sh
```

This will:
- Install OpenClaw globally via npm
- Copy JavaScript skills to `~/.openclaw/skills/`
- Copy workflows to `~/.openclaw/workflows/`
- Start the OpenClaw Gateway

### 2. Verify OpenClaw

```bash
# Check Gateway is running
curl http://localhost:3000/health

# Test integration
python scripts/test_integration.py
```

Expected output:
```
✅ Gateway is running
✅ Got 3 stories from OpenClaw
✅ Got 3 repos from OpenClaw
✅ Aggregated 18 items
```

### 3. Enable OpenClaw

Edit `.env`:
```bash
OPENCLAW_ENABLED=true
```

### 4. Restart Bot

```bash
tech-digest-bot
```

Now you should see:
```
🤖 Starting Tech Digest Bot...
Model: google/gemini-2.0-flash-exp:free
OpenClaw enabled: True
OpenClaw is available - using enhanced research
```

### 5. Test Enhanced Research

Send to your bot:
```
Explain Rust programming language
```

With OpenClaw enabled, the digest will now include:
- ✅ Web search results (DuckDuckGo)
- ✅ HackerNews discussions about Rust
- ✅ GitHub trending Rust repositories
- ✅ Dev.to articles about Rust

Much richer content! 🎉

## Troubleshooting

### Bot Won't Start

**Error: `TELEGRAM_BOT_TOKEN is required`**
- Make sure `.env` file exists
- Check token is copied correctly from BotFather

**Error: `OPENROUTER_API_KEY is required`**
- Sign up at openrouter.ai
- Copy API key to `.env`

### OpenClaw Not Working

**Gateway not running:**
```bash
# Check status
openclaw status

# Start Gateway
openclaw start
```

**Skills not found:**
```bash
# List skills
openclaw skills list

# If empty, copy skills
cp openclaw/skills/*.js ~/.openclaw/skills/
```

**Connection refused:**
```bash
# Test Gateway
curl http://localhost:3000/health

# Should return: {"status":"ok"}
```

### No HackerNews/GitHub Data

```bash
# Verify skills are installed
ls ~/.openclaw/skills/

# Should show:
# devto-trending.js
# github-trending.js
# hackernews-scraper.js
```

## Usage Examples

### Basic Queries
```
Explain GraphQL
What's new in Python 3.13?
How does Kubernetes work?
Latest developments in AI
```

### Follow-up Questions
```
You: Explain WebAssembly
Bot: [Provides digest]

You: How does it compare to JavaScript?
Bot: [Answers with context from previous digest]
```

### Start Fresh
```
/new
```
Clears conversation history, ready for new topic.

## What's Next?

- [Architecture Guide](architecture.md) - Understand how it works
- [OpenClaw Integration](openclaw-integration.md) - Deep dive into OpenClaw
- [Project Structure](project-structure.md) - Code organization

## Development Mode

```bash
# Run from source
python -m tech_digest_bot

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Format code
ruff format src/
```

Enjoy your supercharged tech news bot! 🚀
