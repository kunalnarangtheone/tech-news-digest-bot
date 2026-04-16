# Architecture

## Overview

Tech Digest Bot is a Telegram bot that provides AI-generated tech news digests using web search and optional OpenClaw agent integration.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Telegram User                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Telegram Bot API                        │
│         (python-telegram-bot library)                │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Bot Application                         │
│  ┌─────────────────────────────────────────────┐   │
│  │          Message Handlers                    │   │
│  │  - /start, /help, /new commands              │   │
│  │  - Text message processing                   │   │
│  └────────────────┬─────────────────────────────┘   │
│                   │                                  │
│                   ▼                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │        Research Service                      │   │
│  │  - Orchestrates search providers             │   │
│  │  - Manages OpenClaw availability             │   │
│  │  - Handles conversation context              │   │
│  └────────┬───────────────────────┬──────────────┘   │
│           │                       │                  │
└───────────┼───────────────────────┼──────────────────┘
            │                       │
            ▼                       ▼
┌──────────────────┐    ┌──────────────────────────┐
│  DuckDuckGo      │    │  OpenClaw Agent          │
│  Web Search      │    │  (Optional)              │
│                  │    │  - AI-powered research   │
│  - Real-time     │    │  - CLI subprocess        │
│  - Web results   │    │  - Local embedded mode   │
└──────────────────┘    └──────────────────────────┘
            │                       │
            └───────────┬───────────┘
                        ▼
            ┌──────────────────────┐
            │   LLM Client         │
            │   (Ollama)           │
            │   - Local models     │
            │   - Digest generation│
            └──────────────────────┘
```

## Core Components

### 1. Bot Layer (`src/tech_digest_bot/bot/`)

**Purpose:** Handle Telegram interactions

**Files:**
- `app.py` - Application initialization and configuration
- `handlers.py` - Message and command handlers

**Responsibilities:**
- Receive Telegram messages
- Parse commands (`/start`, `/help`, `/new`)
- Maintain conversation state
- Send formatted responses

### 2. Research Layer (`src/tech_digest_bot/ai/`)

**Purpose:** Coordinate research and content generation

**Files:**
- `research.py` - Research orchestration service
- `llm.py` - LLM client wrapper

**Responsibilities:**
- Determine research strategy (basic vs enhanced)
- Coordinate multiple data sources
- Manage conversation history
- Generate final digests

### 3. Search Layer (`src/tech_digest_bot/search/`)

**Purpose:** Fetch information from various sources

**Files:**
- `duckduckgo.py` - Web search provider
- `openclaw_cli.py` - OpenClaw agent integration

**Responsibilities:**
- Execute web searches (DuckDuckGo)
- Query OpenClaw agent (if enabled)
- Return structured search results

### 4. Configuration (`src/tech_digest_bot/config/`)

**Purpose:** Manage settings and environment

**Files:**
- `settings.py` - Configuration management

**Responsibilities:**
- Load environment variables
- Validate required settings
- Provide configuration to components

## Data Flow

### Basic Research Flow (DuckDuckGo only)

1. User sends message → Telegram Bot
2. Bot → Research Service: `research_topic(topic)`
3. Research Service → DuckDuckGo: `search(topic)`
4. DuckDuckGo → Research Service: Web results
5. Research Service → LLM: Generate digest
6. LLM → Research Service: Generated digest
7. Research Service → Bot: Formatted response
8. Bot → User: Telegram message

### Enhanced Research Flow (with OpenClaw)

1. User sends message → Telegram Bot
2. Bot → Research Service: `research_topic(topic)`
3. Research Service → **Parallel requests:**
   - DuckDuckGo: `search(topic)`
   - OpenClaw CLI: `ask_agent(query)`
4. Both sources → Research Service: Combined results
5. Research Service → LLM: Generate enhanced digest
6. LLM → Research Service: Generated digest
7. Research Service → Bot: Formatted response
8. Bot → User: Telegram message

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Bot Framework | python-telegram-bot | Telegram API interaction |
| Web Search | duckduckgo-search | Real-time web results |
| AI Agent | OpenClaw (optional) | AI-powered research |
| LLM | Ollama | Local LLM inference |
| LLM Model | qwen2.5:7b (default) | Text generation |
| HTTP Client | httpx | Async HTTP requests |
| Environment | python-dotenv | Config management |
| Language | Python 3.14 | Modern Python features |
