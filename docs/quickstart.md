# Quick Start Guide

Get your Tech Digest Bot running in 5 minutes.

## Prerequisites

- Python 3.14+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- [Ollama](https://ollama.ai/) installed and running
- (Optional) OpenClaw for enhanced research

## Installation

```bash
# Navigate to project
cd tech-news-digest-bot

# Install dependencies
pip install -e .

# Or with uv (recommended)
uv sync
```

## Configuration

```bash
# 1. Start Ollama (in a separate terminal)
ollama serve

# 2. Pull a model (recommended: qwen2.5:7b)
ollama pull qwen2.5:7b

# 3. Configure environment
# Edit .env with your bot token
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

## Run the Bot

```bash
# Option 1: Use the run script
./run_bot.sh

# Option 2: Direct command
source .venv/bin/activate
python -m tech_digest_bot
```

You should see:
```
🤖 Starting Tech Digest Bot...
Provider: Ollama (Local)
Model: qwen2.5:7b
Ollama URL: http://localhost:11434/v1
OpenClaw enabled: False
Press Ctrl+C to stop
```

## Test It

1. Open Telegram and find your bot
2. Send `/start`
3. Ask a question: `What's new in Rust?`
4. Get a comprehensive digest!

## OpenClaw Integration (Optional)

For enhanced AI-powered research:

### Enable OpenClaw

```bash
# 1. Start OpenClaw gateway
openclaw start

# 2. Edit .env
OPENCLAW_ENABLED=true

# 3. Restart the bot
./run_bot.sh
```

Now you should see:
```
🤖 Starting Tech Digest Bot...
Provider: Ollama (Local)
Model: qwen2.5:7b
OpenClaw enabled: True
OpenClaw is available - using enhanced research
```

## How It Works

### Without OpenClaw (Basic Mode)
- Uses **DuckDuckGo** for web search
- LLM generates digest from search results
- Fast and reliable

### With OpenClaw (Enhanced Mode)
- Uses **DuckDuckGo** for web search
- Uses **OpenClaw Agent** for AI-powered research
- LLM synthesizes both sources
- More comprehensive results

## Commands

- `/start` - Welcome message
- `/help` - Show available commands
- `/new` - Start a new conversation

## Usage Examples

### Basic Queries
```
What's new in Python?
Explain GraphQL
How does Kubernetes work?
Latest developments in AI
```

### Follow-up Questions
```
You: Explain WebAssembly
Bot: [Provides digest]

You: How does it compare to JavaScript?
Bot: [Answers with context]
```

## Troubleshooting

### Bot Won't Start

**Error: `TELEGRAM_BOT_TOKEN is required`**
- Make sure `.env` file exists
- Check token is correct

**Error: Ollama connection failed**
- Make sure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Verify OLLAMA_BASE_URL in `.env`

### OpenClaw Not Working

**Check if OpenClaw is running:**
```bash
openclaw status
```

Should show "running" in output.

**Disable OpenClaw if not needed:**
```bash
# In .env file
OPENCLAW_ENABLED=false
```

The bot works great without OpenClaw using DuckDuckGo search.

### Multiple Bot Instances Error

```
Error: Conflict: terminated by other getUpdates request
```

**Solution:** Stop all instances:
```bash
pkill -f "tech-digest-bot"
pkill -f "python -m tech_digest_bot"
```

Then start fresh with `./run_bot.sh`

## Next Steps

- [Architecture](architecture.md) - Understand how it works

## Development Mode

```bash
# Run from source
python -m tech_digest_bot

# Type checking
make typecheck

# Linting
make lint

# Format code
make format

# Clean generated files
make clean
```

Enjoy your tech digest bot! 🚀
