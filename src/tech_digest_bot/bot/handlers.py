"""Telegram bot message handlers."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ..ai import ResearchService

logger = logging.getLogger(__name__)


class BotHandlers:
    """Collection of Telegram bot handlers."""

    def __init__(self, research_service: ResearchService) -> None:
        """
        Initialize handlers.

        Args:
            research_service: Research service instance
        """
        self.research = research_service
        self.conversation_history: dict[int, list[dict[str, str]]] = {}

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        if not update.message:
            return

        welcome_message = (
            "🤖 *Welcome to Tech Digest Bot!*\n\n"
            "I'm your AI-powered research assistant. I can:\n\n"
            "📚 Research any tech topic\n"
            "🔍 Search the web for latest information\n"
            "📝 Generate concise 2-minute digests\n"
            "💬 Answer your follow-up questions\n\n"
            "*How to use:*\n\n"
            "Just send me a tech topic and I'll research it!\n\n"
            "Examples:\n"
            "• `Explain WebAssembly`\n"
            "• `What's new in Python 3.13?`\n"
            "• `How does Kubernetes work?`\n"
            "• `Latest developments in AI`\n\n"
            "After I provide a digest, feel free to ask "
            "follow-up questions!\n\n"
            "Use /help to see all commands."
        )
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        if not update.message:
            return

        help_message = (
            "🤖 *Tech Digest Bot - Help*\n\n"
            "*Available Commands:*\n\n"
            "🆕 /start\n"
            "   Start the bot and see welcome message\n\n"
            "❓ /help\n"
            "   Show this help message\n\n"
            "🔄 /new\n"
            "   Start a new conversation (clears history)\n\n"
            "*How to use:*\n\n"
            "1️⃣ Send me any tech topic you want to learn about\n"
            "   Example: `Explain GraphQL`\n\n"
            "2️⃣ I'll search the web and create a 2-minute digest\n\n"
            "3️⃣ Ask follow-up questions to dive deeper\n"
            "   Example: `How does it compare to REST?`\n\n"
            "4️⃣ Use /new to start researching a new topic\n\n"
            "*Tips:*\n"
            "• Be specific for better results\n"
            "• I can explain concepts, compare technologies, "
            "or discuss trends\n"
            "• Follow-up questions keep the context from previous digest"
        )
        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def new_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /new command - clear conversation history."""
        if not update.message or not update.effective_user:
            return

        user_id = update.effective_user.id
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

        await update.message.reply_text(
            "✅ *New conversation started!*\n\n"
            "Your previous conversation history has been cleared.\n"
            "Send me a tech topic to research!",
            parse_mode="Markdown",
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle text messages - research topics or answer questions."""
        if not update.message or not update.effective_user:
            return

        user_message = update.message.text
        if not user_message:
            return

        user_id = update.effective_user.id

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Check if user has conversation history
        has_history = (
            user_id in self.conversation_history
            and len(self.conversation_history[user_id]) > 0
        )

        # Determine if this is a new topic or follow-up question
        is_followup = has_history and not any(
            keyword in user_message.lower()
            for keyword in [
                "explain",
                "what is",
                "tell me about",
                "research",
                "learn about",
            ]
        )

        if is_followup:
            # Answer as follow-up question
            logger.info(
                "Follow-up question from user %d: %s", user_id, user_message
            )
            response = await self.research.answer_followup(
                user_message, self.conversation_history[user_id]
            )

            # Update history
            self.conversation_history[user_id].append(
                {"role": "user", "content": user_message}
            )
            self.conversation_history[user_id].append(
                {"role": "assistant", "content": response}
            )

        else:
            # Research new topic
            logger.info(
                "New research request from user %d: %s", user_id, user_message
            )

            # Send initial message
            status_msg = await update.message.reply_text(
                "🔍 *Researching...*\n\n"
                "Searching the web for information...",
                parse_mode="Markdown",
            )

            # Generate digest
            response = await self.research.research_topic(user_message)

            # Delete status message
            await status_msg.delete()

            # Initialize or update conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            self.conversation_history[user_id].append(
                {"role": "user", "content": f"Research: {user_message}"}
            )
            self.conversation_history[user_id].append(
                {"role": "assistant", "content": response}
            )

            # Limit history to last 10 messages
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = self.conversation_history[
                    user_id
                ][-10:]

        # Send response
        await update.message.reply_text(
            response, parse_mode="Markdown", disable_web_page_preview=True
        )

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle errors."""
        logger.error("Update %s caused error: %s", update, context.error)

        if update and update.message:
            await update.message.reply_text(
                "❌ *Error*\n\n"
                "Sorry, something went wrong processing your request.\n"
                "Please try again or use /new to start fresh.",
                parse_mode="Markdown",
            )
