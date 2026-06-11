# 🤖 AI adversarial chatbot

An adversarial AI chatbot assistant powered by LangChain, FastAPI, Next.js, and **Groq**.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## ✨ Features

### 🧠 **Intelligent Research Agent**

- **LangChain Agent** with web search capabilities
- **DuckDuckGo Search** for finding current tech information
- **Groq LLM** for fast, high-quality answer synthesis
- **Streaming Responses** with Server-Sent Events

### 🔍 **Web Research**

- **Multi-Source Search** across tech news and articles
- **Intelligent Answer Synthesis** combining multiple sources
- **Context-Aware Follow-ups** maintaining conversation history

### ⚡ **Performance**
- **Average Response Time:** 3-8 seconds with Groq
- **Knowledge Graph Queries:** < 1 second
- **Automatic Caching:** Previously searched topics return instantly
- **Streaming Responses:** Real-time SSE for progressive rendering
- **Weekly Backups:** GitHub Actions backup to repository

### 🌐 **Modern Web Stack**
- **FastAPI Backend:** RESTful API with SSE streaming
- **Next.js Frontend:** React with Server-Side Rendering
- **Vercel AI SDK:** Chat interface with streaming support
- **Tailwind CSS:** Modern, responsive UI
- **Session Management:** Persistent conversations

### 🤖 **Powered by Groq**
- **Ultra-fast cloud inference** with free tier
- **llama-3.3-70b-versatile**: High quality responses
- **No local LLM setup required**

## 🚀 Quick Start

### Prerequisites

- **Python 3.14+**
- **Node.js 20+** and npm (Next.js requirement)
- **Groq API Key** (free) - [Get API key](https://console.groq.com/)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/tech-news-digest-bot.git
cd tech-news-digest-bot

# Install backend dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install frontend dependencies
cd frontend
npm install
```

### Configuration

#### Backend (.env)

Create `.env` file in the root directory:

```bash
# Groq LLM (get free API key from https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# LangChain Agent
USE_LANGCHAIN_AGENT=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
SESSION_TTL_HOURS=24
```

#### Frontend (frontend/.env.local)

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Application

#### Option 1: Docker (Recommended)

**Fastest way to get started:**

```bash
# Copy environment template
cp .env.docker .env

# Edit .env and add your API keys
nano .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

Then open http://localhost:3000 in your browser.

See [Docker Deployment Guide](docs/DOCKER.md) for details.

#### Option 2: Development Mode

**Terminal 1 - Backend:**
```bash
uvicorn tech_digest_bot.api.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:3000 in your browser.

#### Option 3: Using Makefile

```bash
# Start backend
make run-api

# Start frontend (in new terminal)
make run-frontend
```

### API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

## 📖 Usage

### Web Interface

1. Open http://localhost:3000
2. Type your tech question or click an example prompt
3. Watch the AI research and stream the response in real-time
4. Click "New Chat" to start a fresh conversation

### API Usage

**Non-streaming:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Rust programming language?"}'
```

**Streaming (SSE):**
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Next.js App Router"}'
```

**Create Session:**
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │  ← User Interface (React + Tailwind)
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP + SSE
         ↓
┌─────────────────┐
│   FastAPI       │  ← RESTful API + Streaming
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────────┐
│  Groq   │ │  DuckDuckGo  │
│   LLM   │ │    Search    │
└─────────┘ └──────────────┘
```

### Key Components

- **Frontend:** Next.js 16 with App Router, Vercel AI SDK, Tailwind CSS
- **Backend:** FastAPI with SSE streaming, session management
- **AI Engine:** ResearchService with LangChain agent
- **LLM:** Groq cloud API (llama-3.3-70b-versatile)
- **Search:** DuckDuckGo for web research

## 📁 Project Structure

```
tech-news-digest-bot/
├── src/tech_digest_bot/
│   ├── api/                      # FastAPI application
│   │   ├── main.py               # App entry + lifespan
│   │   ├── session.py            # Session management
│   │   ├── streaming.py          # SSE utilities
│   │   ├── models/               # Request/response models
│   │   └── routes/               # API endpoints
│   ├── ai/                       # AI/research logic
│   │   ├── research.py           # Research service
│   │   ├── llm.py                # Groq LLM client
│   │   ├── agent.py              # LangChain agent
│   │   └── tools/                # Agent tools
│   ├── search/                   # Search providers
│   │   └── duckduckgo.py         # DuckDuckGo client
│   └── config/                   # Configuration
│       ├── settings.py           # Pydantic settings
│       └── constants.py          # Constants
├── frontend/                     # Next.js application
│   ├── app/                      # Pages (App Router)
│   ├── components/               # React components
│   ├── hooks/                    # Custom hooks
│   ├── lib/                      # API client + utils
│   └── types/                    # TypeScript types
├── tests/                        # Test suite
├── scripts/                      # Utility scripts
└── docs/                         # Documentation
```

## 🧪 Testing

### Quick Commands (using Make)

```bash
# Run all pre-Docker checks (recommended before building)
make check

# Run individual checks
make lint              # Check code style
make test              # Run tests
make test-cov          # Run with coverage report

# Auto-fix issues
make lint-fix          # Auto-fix code style issues
make format            # Format code

# Pre-commit workflow
make pre-commit        # Format + check (run before committing)
```

### Direct pytest Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tech_digest_bot

# Run specific test file
pytest tests/unit/test_settings.py

# Verbose output
pytest -v
```

## 📚 Documentation

- [Docker Deployment Guide](docs/DOCKER.md) - Docker and Docker Compose setup
- [Migration Guide](docs/MIGRATION_COMPLETE.md) - Web application migration guide
- [Feature Research](docs/FEATURE_RESEARCH.md) - Feature planning
- [Test Updates](docs/TEST_UPDATES.md) - Testing documentation

## 🔧 Development

### Backend Development

**Quick Setup:**

```bash
# Install dependencies with dev tools
make install-dev

# Run all checks before Docker build
make check
```

**Development Commands:**

```bash
# Code quality
make lint              # Check code style
make lint-fix          # Auto-fix style issues
make format            # Format code
make test              # Run tests
make test-cov          # Run with coverage

# Pre-commit workflow
make pre-commit        # Format + lint + test
```

**Direct Commands:**

```bash
# Run with auto-reload
uvicorn tech_digest_bot.api.main:app --reload

# Manual checks
ruff check src/        # Lint
ruff format src/       # Format
pytest                 # Test
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Or use Make:

```bash
make install-frontend  # Install dependencies
```

## 📦 Deployment

### Backend (Railway / Fly.io / DigitalOcean)

```bash
# Build Docker image
docker build -t tech-digest-api .

# Run container
docker run -p 8000:8000 --env-file .env tech-digest-api
```

### Frontend (Vercel)

```bash
# Deploy to Vercel
cd frontend
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

## 🔑 Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `GROQ_API_KEY` - Groq API key

**Optional:**
- `API_HOST`, `API_PORT` - API server configuration
- `CORS_ORIGINS` - Allowed frontend origins
- `SESSION_TTL_HOURS` - Session expiration time
- `GROQ_MODEL` - LLM model selection
- `USE_LANGCHAIN_AGENT` - Enable/disable agent

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- **LangChain** - Agent framework
- **Groq** - Ultra-fast LLM inference
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **Vercel** - AI SDK for streaming chat

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.
