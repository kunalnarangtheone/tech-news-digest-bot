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
from ..search import OpenClawCLIClient
from .handlers import BotHandlers

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

        # Initialize Ollama LLM client
        self.llm_client = LLMClient(
            model=self.settings.ollama_model,
            base_url=self.settings.ollama_base_url,
        )

        # Initialize OpenClaw CLI if enabled
        openclaw_client = None
        if self.settings.openclaw_enabled:
            openclaw_client = OpenClawCLIClient()

        self.research_service = ResearchService(
            llm_client=self.llm_client,
            openclaw_client=openclaw_client,
        )

        self.handlers = BotHandlers(research_service=self.research_service)

    async def post_init(self, application: Application) -> None:
        """Post-initialization hook."""
        # Initialize research service (check OpenClaw availability)
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
        logger.info("Provider: Ollama (Local)")
        logger.info("Model: %s", self.settings.ollama_model)
        logger.info("Ollama URL: %s", self.settings.ollama_base_url)
        logger.info("OpenClaw enabled: %s", self.settings.openclaw_enabled)
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

    # Create and run bot
    bot = TechDigestBot()
    bot.run()


if __name__ == "__main__":
    main()
