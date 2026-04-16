# Architecture

## Overview

Tech Digest Bot is a modular Python application with optional JavaScript integration for browser automation via OpenClaw.

```
┌─────────────────────────────────────────────────────┐
│                  Telegram User                       │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Messages
                 ▼
┌─────────────────────────────────────────────────────┐
│              Telegram Bot (Python)                   │
│  ┌──────────────────────────────────────────────┐  │
│  │         BotHandlers                          │  │
│  │  • /start, /help, /new                       │  │
│  │  • Message routing                           │  │
│  │  • Conversation history                      │  │
│  └────────────┬─────────────────────────────────┘  │
└───────────────┼────────────────────────────────────┘
                │
                │ Research requests
                ▼
┌─────────────────────────────────────────────────────┐
│           ResearchService (Python)                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  • Coordinates search providers              │  │
│  │  • Aggregates results                        │  │
│  │  • Manages LLM interaction                   │  │
│  └──┬───────────────────────────────────────┬───┘  │
└─────┼───────────────────────────────────────┼──────┘
      │                                       │
      │                                       │
      ▼                                       ▼
┌──────────────────┐              ┌────────────────────┐
│  DuckDuckGoSearch│              │  OpenClawClient    │
│    (Python)      │              │    (Python)        │
│                  │              │                    │
│  • Web search    │              │  • HTTP API client │
│  • No API key    │              │  • Skill executor  │
│  • Always works  │              │  • Optional        │
└──────────────────┘              └────────┬───────────┘
                                           │
                                           │ HTTP API
                                           ▼
                               ┌────────────────────────┐
                               │  OpenClaw Gateway      │
                               │    (Node.js)           │
                               │                        │
                               │  • Browser automation  │
                               │  • Puppeteer/CDP       │
                               │  • Skill registry      │
                               └────────┬───────────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         │              │              │
                         ▼              ▼              ▼
                  ┌──────────┐  ┌──────────┐  ┌──────────┐
                  │HackerNews│  │  GitHub  │  │ Dev.to   │
                  │  Skill   │  │  Skill   │  │  Skill   │
                  │  (.js)   │  │  (.js)   │  │  (.js)   │
                  └──────────┘  └──────────┘  └──────────┘
```

## Components

### Bot Layer (`src/tech_digest_bot/bot/`)

**BotHandlers**: Telegram message handlers
- Command handlers: `/start`, `/help`, `/new`
- Message handler: processes user queries
- Conversation history management
- Error handling

**TechDigestBot**: Application orchestrator
- Initializes all services
- Configures Telegram Application
- Manages app lifecycle

### AI Layer (`src/tech_digest_bot/ai/`)

**LLMClient**: OpenRouter LLM interface
- Digest generation
- Follow-up Q&A
- Prompt management
- Model abstraction

**ResearchService**: Multi-source research coordinator
- Orchestrates search providers
- Aggregates results
- Context building
- Fallback handling

### Search Layer (`src/tech_digest_bot/search/`)

**DuckDuckGoSearch**: Web search provider
- Free, no API key required
- Always available
- Fallback option

**OpenClawClient**: Browser automation interface
- HTTP client for OpenClaw Gateway
- Skill execution
- Multi-source aggregation
- Optional, graceful degradation

### Config Layer (`src/tech_digest_bot/config/`)

**Settings**: Configuration management
- Environment variable loading
- Validation
- Default values
- Singleton pattern

### Models Layer (`src/tech_digest_bot/models/`)

**Type Definitions**: TypedDict models
- `SearchResult`
- `HackerNewsStory`
- `GitHubRepo`
- `DevToArticle`
- `TechNews`

## Data Flow

### Basic Research (No OpenClaw)

```
User Query
  → BotHandlers
  → ResearchService
  → DuckDuckGoSearch.search()
  → LLMClient.generate_digest()
  → User Response
```

### Enhanced Research (With OpenClaw)

```
User Query
  → BotHandlers
  → ResearchService
  → Parallel:
      - DuckDuckGoSearch.search()
      - OpenClawClient.aggregate_tech_news()
          → HTTP → OpenClaw Gateway
          → Parallel JS Skills:
              - hackernews-scraper.js
              - github-trending.js
              - devto-trending.js
          → Results aggregated
  → Context built from all sources
  → LLMClient.generate_digest()
  → User Response
```

## OpenClaw Integration

### JavaScript Skills (`openclaw/skills/`)

Browser automation scripts executed by OpenClaw:
- `hackernews-scraper.js`: Puppeteer-based HN scraping
- `github-trending.js`: GitHub trending page scraping
- `devto-trending.js`: Dev.to article scraping

### JavaScript Workflows (`openclaw/workflows/`)

Cron-scheduled automation:
- `daily-digest-workflow.js`: Daily aggregated news
- `topic-monitor-workflow.js`: Topic trend monitoring

### Communication

Python ↔ OpenClaw via HTTP:
- `POST /api/skills/execute`: Execute a skill
- `GET /health`: Gateway health check

## Error Handling

1. **Graceful Degradation**: If OpenClaw unavailable, fallback to DuckDuckGo only
2. **Exception Handling**: All async operations wrapped in try/except
3. **User Feedback**: Clear error messages to users
4. **Logging**: Comprehensive logging at all layers

## Configuration Precedence

1. Environment variables (`.env`)
2. Default values in `Settings`

## Type Safety

- Strict type hints throughout
- TypedDict for data models
- mypy type checking in CI

## Testing Strategy

- Unit tests for each component
- Integration tests for OpenClaw
- Mock external services (Telegram, OpenRouter)
- Pytest with async support

## Scalability Considerations

- Stateless handlers (conversation history in memory)
- Parallel search execution
- OpenClaw Gateway can run on separate server
- LRU cache for settings

## Security

- No hardcoded credentials
- Environment-based configuration
- Input validation on user messages
- Rate limiting via Telegram's built-in mechanism
