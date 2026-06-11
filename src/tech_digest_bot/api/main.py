"""FastAPI application for Tech Digest Bot."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tech_digest_bot.ai.llm import LLMClient
from tech_digest_bot.ai.research import ResearchService
from tech_digest_bot.api.routes import chat, health, sessions
from tech_digest_bot.api.session import SessionStore
from tech_digest_bot.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances
research_service: ResearchService | None = None
session_store: SessionStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global research_service, session_store

    # Startup
    logger.info("Starting Tech Digest API...")

    settings = get_settings()

    # Initialize LLM client
    llm_client = LLMClient(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
    )

    # Initialize Research Service
    research_service = ResearchService(
        llm_client=llm_client,
        use_agent=settings.use_langchain_agent,
        settings=settings,
    )

    # Initialize research service (Neo4j connections, etc.)
    await research_service.initialize()

    logger.info(
        f"Research service initialized "
        f"(model={settings.groq_model}, agent={settings.use_langchain_agent})"
    )

    # Initialize Session Store
    session_store = SessionStore(
        use_sqlite=True,
        ttl_hours=settings.session_ttl_hours,
    )

    # Inject dependencies into routes
    chat.set_dependencies(session_store, research_service)
    sessions.set_session_store(session_store)

    logger.info("Tech Digest API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Tech Digest API...")

    if research_service:
        await research_service.cleanup()

    logger.info("Tech Digest API shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Tech Digest API",
    description="AI-powered tech news research API with streaming responses",
    version="0.4.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Tech Digest API",
        "version": "0.4.0",
        "description": "AI-powered tech news research API",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "tech_digest_bot.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
