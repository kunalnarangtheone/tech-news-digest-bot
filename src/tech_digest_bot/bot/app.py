"""Main Telegram bot application."""

import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from ..ai import LLMClient, ResearchService
from ..config import get_settings
from .handlers import BotHandlers

# Optional DI container support
try:
    from ..container import create_container
    DI_AVAILABLE = True
except ImportError:
    DI_AVAILABLE = False

logger = logging.getLogger(__name__)


class TechDigestBot:
    """Tech Digest Telegram Bot application."""

    def __init__(self) -> None:
        """Initialize the bot application."""
        # Load settings
        self.settings = get_settings()

        # Validate settings
        is_valid, errors = self.settings.validate()
        if not is_valid:
            logger.error("Invalid configuration:")
            for error in errors:
                logger.error("  - %s", error)
            sys.exit(1)

        # Initialize Groq LLM client
        self.llm_client = LLMClient(
            model=self.settings.groq_model,
            api_key=self.settings.groq_api_key,
        )

        # Initialize Research Service with LangChain agent
        self.research_service = ResearchService(
            llm_client=self.llm_client,
            use_agent=self.settings.use_langchain_agent,
            settings=self.settings,
        )

        self.handlers = BotHandlers(research_service=self.research_service)

    async def post_init(self, application: Application) -> None:
        """Post-initialization hook."""
        # Initialize research service (LangChain agent)
        await self.research_service.initialize()

    def create_application(self) -> Application:
        """
        Create and configure the Telegram application.

        Returns:
            Configured Application instance
        """
        # Create application
        application = (
            Application.builder()
            .token(self.settings.telegram_bot_token)
            .post_init(self.post_init)
            .build()
        )

        # Register handlers
        application.add_handler(
            CommandHandler("start", self.handlers.start_command)
        )
        application.add_handler(
            CommandHandler("help", self.handlers.help_command)
        )
        application.add_handler(
            CommandHandler("new", self.handlers.new_command)
        )

        # Register message handler for regular text
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handlers.handle_message
            )
        )

        # Register error handler
        application.add_error_handler(self.handlers.error_handler)

        return application

    def run(self) -> None:
        """Start the bot."""
        logger.info("🤖 Starting Tech Digest Bot...")
        logger.info("=" * 60)
        logger.info("Provider: Groq (Cloud)")
        logger.info("Model: %s", self.settings.groq_model)
        logger.info("LangChain Agent: %s", self.settings.use_langchain_agent)
        if self.settings.use_langchain_agent:
            logger.info("  - Neo4j URI: %s", self.settings.neo4j_uri)
            logger.info(
                "  - Embedding Model: %s", self.settings.embedding_model
            )
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop")

        # Create and run application
        application = self.create_application()
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Main entry point for the bot."""
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Optional: Use DI container if available
    if DI_AVAILABLE:
        create_container()
        logger.info("Using dependency injection container")

    # Create and run bot (DI wiring happens automatically if enabled)
    bot = TechDigestBot()
    bot.run()


if __name__ == "__main__":
    main()
