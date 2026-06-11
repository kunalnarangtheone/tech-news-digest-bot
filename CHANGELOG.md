# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-06-10

### Added
- **FastAPI Backend** - RESTful API with SSE streaming support
- **Next.js Frontend** - Modern web interface with React and Tailwind CSS
- **Docker Support** - Full Docker and Docker Compose configuration
  - Multi-stage builds for optimized images
  - Health checks for all services
  - Volume persistence for data and models
  - Development and production configurations
- **API Endpoints**:
  - `GET /api/health` - Health check
  - `POST /api/sessions/` - Create session
  - `DELETE /api/sessions/{id}` - Delete session
  - `POST /api/chat` - Non-streaming chat
  - `POST /api/chat/stream` - Streaming chat with SSE
- **Session Management** - UUID-based sessions with SQLite persistence
- **Streaming Responses** - Server-Sent Events for progressive rendering
- **Web UI Components**:
  - ChatInterface - Main chat container
  - ChatMessage - iMessage-style message bubbles
  - ChatInput - Auto-resize textarea with send button
  - ChatHeader - Header with "New Chat" button
- **API Configuration** - New settings: `API_HOST`, `API_PORT`, `CORS_ORIGINS`, `SESSION_TTL_HOURS`
- **Documentation**:
  - `docs/DOCKER.md` - Docker deployment guide
  - `docs/MIGRATION_COMPLETE.md` - Migration guide
  - `docs/TELEGRAM_REMOVAL.md` - Telegram removal summary
  - Swagger/OpenAPI docs at `/docs`

### Changed
- **Project Description** - Now "AI-powered tech news research API" (was "bot")
- **Keywords** - Replaced "telegram", "bot" with "web", "api", "fastapi", "nextjs"
- **Entry Point** - Changed from `tech_digest_bot.bot.app:main` to `tech_digest_bot.api.main:main`
- **README.md** - Complete rewrite focusing on web application
- **Makefile** - Updated targets for API and frontend
- **Tests** - Updated to remove Telegram dependencies

### Removed
- **Telegram Bot** - Entire Telegram interface (archived to `archive/telegram-bot-deprecated/`)
- **Telegram Dependency** - Removed `python-telegram-bot>=21.0`
- **Telegram Settings** - Removed `telegram_bot_token`, `telegram_channel_id`, `telegram_alert_chat`
- **Telegram Environment Variables** - Removed from `.env` and `.env.example`

### Preserved (90% Code Reuse)
- **AI/Research Stack** - All AI services, LangChain agent, and tools
- **Neo4j Integration** - Knowledge graph storage and queries
- **Groq LLM Client** - Fast cloud inference
- **DuckDuckGo Search** - Web search capabilities
- **Prompt Templates** - All prompt engineering
- **Configuration** - Core settings and constants

### Migration
- Migrated from Telegram bot to web application
- All AI capabilities preserved and enhanced with streaming
- Session management redesigned for web
- RESTful API enables multiple client types (web, mobile, CLI)

### Technical Debt Paid
- Removed platform-specific coupling (Telegram)
- Separated interface layer from business logic
- Added proper API documentation (Swagger)
- Improved testability and local development

## [0.4.0] - 2026-05-XX

### Added
- Groq LLM integration for ultra-fast inference
- LangChain agent with intelligent tool routing
- Neo4j Aura knowledge graph with BM25 search
- Automatic topic extraction and relationship discovery

### Changed
- Switched from local Ollama to Groq cloud API
- Simplified deployment (no local LLM needed)
- Improved response time (3-8 seconds average)

## [0.3.0] - 2026-04-XX

### Added
- Neo4j vector store integration
- Persistent knowledge graph
- Incremental learning from searches

## [0.2.0] - 2026-03-XX

### Added
- DuckDuckGo web search integration
- Basic digest generation
- Conversation history

## [0.1.0] - 2026-02-XX

### Added
- Initial Telegram bot
- Basic LLM integration
- Simple Q&A functionality

---

## Migration Notes

### v0.4.0 → v0.5.0 (Telegram → Web)

**Breaking Changes:**
- Telegram bot removed (use web interface instead)
- `TELEGRAM_BOT_TOKEN` no longer required
- Entry point changed from `tech-digest-bot` to `tech-digest-api`

**Migration Steps:**
1. Pull latest code
2. Install dependencies: `pip install -e .`
3. Install frontend: `cd frontend && npm install`
4. Update `.env` - remove Telegram vars, add API vars
5. Run backend: `uvicorn tech_digest_bot.api.main:app --reload`
6. Run frontend: `cd frontend && npm run dev`
7. Access at http://localhost:3000

**Rollback:**
Telegram code archived in `archive/telegram-bot-deprecated/` - can be restored if needed.

---

## Upgrade Guide

### From v0.4.0 (Telegram) to v0.5.0 (Web)

**Step 1: Update Dependencies**
```bash
git pull
pip install -e .
cd frontend && npm install
```

**Step 2: Update Configuration**

Remove from `.env`:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHANNEL_ID=...
TELEGRAM_ALERT_CHAT=...
```

Add to `.env`:
```
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
SESSION_TTL_HOURS=24
```

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Step 3: Run New Application**
```bash
# Terminal 1
uvicorn tech_digest_bot.api.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

**Step 4: Test**
Open http://localhost:3000 and try asking a question.

---

## Future Roadmap

### v0.6.0 (Planned)
- [ ] User authentication (JWT)
- [ ] Conversation history UI
- [ ] Export conversations (Markdown/PDF)
- [ ] Native Groq streaming integration
- [ ] Markdown rendering in chat

### v0.7.0 (Planned)
- [ ] Mobile app (React Native)
- [ ] Voice input (Web Speech API)
- [ ] Share conversations
- [ ] Analytics dashboard

### v1.0.0 (Planned)
- [ ] Production deployment
- [ ] PostgreSQL for sessions
- [ ] Redis caching
- [ ] Monitoring and logging (Sentry)
- [ ] Rate limiting
- [ ] API versioning
