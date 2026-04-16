# Tech Digest Bot - Project Structure

Modern Python codebase with OpenClaw integration.

```
tech-digest-bot/
│
├── src/tech_digest_bot/          # Main Python package
│   ├── __init__.py                # Package exports
│   ├── __main__.py                # CLI entry point
│   │
│   ├── bot/                       # Telegram bot layer
│   │   ├── __init__.py
│   │   ├── app.py                 # Main bot application
│   │   └── handlers.py            # Message handlers
│   │
│   ├── ai/                        # AI & research layer
│   │   ├── __init__.py
│   │   ├── llm.py                 # LLM client (OpenRouter)
│   │   └── research.py            # Multi-source research service
│   │
│   ├── search/                    # Search providers
│   │   ├── __init__.py
│   │   ├── duckduckgo.py          # DuckDuckGo search
│   │   └── openclaw.py            # OpenClaw HTTP client
│   │
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py            # Settings with validation
│   │
│   └── models/                    # Type definitions
│       ├── __init__.py
│       └── types.py               # TypedDict models
│
├── openclaw/                      # OpenClaw resources (JavaScript)
│   ├── skills/                    # Browser automation skills
│   │   ├── hackernews-scraper.js  # HackerNews scraping
│   │   ├── github-trending.js     # GitHub trending scraping
│   │   └── devto-trending.js      # Dev.to scraping
│   │
│   └── workflows/                 # Cron workflows
│       ├── daily-digest-workflow.js    # Daily digest automation
│       └── topic-monitor-workflow.js   # Topic monitoring
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   └── test_config.py             # Config tests
│
├── docs/                          # Documentation
│   ├── quickstart.md              # Quick start guide
│   ├── architecture.md            # Architecture overview
│   └── openclaw-integration.md    # OpenClaw setup guide
│
├── scripts/                       # Utility scripts
│   ├── test_integration.py        # Test OpenClaw integration
│   └── setup_openclaw.sh          # OpenClaw setup script
│
├── .env.example                   # Environment template
├── .env                           # Local config (gitignored)
├── .gitignore
├── .python-version
├── pyproject.toml                 # Python project config
└── README.md                      # Main documentation
```

## Key Design Principles

### 1. Separation of Concerns
- **Bot layer**: Telegram-specific logic only
- **AI layer**: LLM and research orchestration
- **Search layer**: Provider implementations
- **Config layer**: Centralized settings
- **Models layer**: Type definitions

### 2. Type Safety
- Strict type hints throughout
- TypedDict for data structures
- mypy type checking
- Modern Python 3.14 features

### 3. Modularity
- Each component is independently testable
- Clear interfaces between layers
- Dependency injection
- Optional OpenClaw integration

### 4. Graceful Degradation
- Works without OpenClaw (DuckDuckGo only)
- Fallback on errors
- Clear error messages

## Data Flow

```
User Message (Telegram)
  ↓
BotHandlers.handle_message()
  ↓
ResearchService.research_topic()
  ↓
├─→ DuckDuckGoSearch.search()        [Always]
└─→ OpenClawClient.aggregate_tech_news()  [Optional]
     ↓ HTTP
    OpenClaw Gateway (Node.js)
     ↓
    JavaScript Skills (Browser Automation)
     ↓
    HackerNews + GitHub + Dev.to
  ↓
LLMClient.generate_digest()
  ↓
Response to User
```

## Technologies

**Python Stack:**
- python-telegram-bot: Telegram bot framework
- openai: OpenRouter LLM client
- duckduckgo-search: Web search
- aiohttp: Async HTTP client
- python-dotenv: Environment management

**JavaScript Stack (OpenClaw):**
- OpenClaw: Browser automation framework
- Puppeteer: Headless Chrome control
- Node.js: Runtime environment

**Development:**
- pytest: Testing framework
- mypy: Static type checking
- ruff: Linting and formatting

## Running the Bot

### Development
```bash
# Basic (no OpenClaw)
python -m tech_digest_bot

# With OpenClaw
./scripts/setup_openclaw.sh
python -m tech_digest_bot
```

### Production
```bash
# Install
pip install -e .

# Run
tech-digest-bot
```

## Testing

```bash
# Unit tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Integration test
python scripts/test_integration.py
```

## Configuration

All config via environment variables:
- `.env.example`: Template with all options
- `.env`: Local config (gitignored)
- Settings class validates on startup

## OpenClaw Integration

**Python Side:**
- `OpenClawClient`: HTTP client
- Calls skills via REST API
- Aggregates results

**JavaScript Side:**
- Skills in `openclaw/skills/`
- Workflows in `openclaw/workflows/`
- Executed by OpenClaw Gateway

**Communication:**
```
Python (OpenClawClient)
  → HTTP POST /api/skills/execute
  → OpenClaw Gateway
  → Execute JavaScript skill
  → Return results as JSON
  → Python processes results
```
