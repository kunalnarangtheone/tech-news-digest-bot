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

    async def _is_topic_change(
        self, user_message: str, history: list[dict[str, str]]
    ) -> bool:
        """
        Detect if the new message is a topic change or genuine follow-up.

        Args:
            user_message: Current user message
            history: Conversation history

        Returns:
            True if this is a new topic, False if it's a follow-up
        """
        if not history:
            return True

        # Get last few user messages to understand the context
        recent_user_messages = [
            msg["content"] for msg in history[-4:] if msg["role"] == "user"
        ]

        if not recent_user_messages:
            return True

        # Use the research service to detect topic change
        return await self.research.is_topic_change(
            user_message, recent_user_messages
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

        # Initialize conversation history if needed
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Get current conversation history
        history = self.conversation_history[user_id]

        logger.info("Processing message from user %d: %s", user_id, user_message)

        # Send initial status message
        status_msg = await update.message.reply_text(
            "🔍 *Researching...*\n\n" "Searching for information...",
            parse_mode="Markdown",
        )

        # Detect if this is a topic change
        is_new_topic = await self._is_topic_change(user_message, history)

        if is_new_topic and history:
            # Topic changed - clear history and start fresh
            logger.info("Topic change detected, clearing history")
            self.conversation_history[user_id] = []
            history = []

        # Let the LLM decide if it needs to search or can answer from context
        if history:
            # Pass conversation history - LLM will decide if it needs new search
            response = await self.research.answer_followup(user_message, history)
        else:
            # New conversation - research the topic
            response = await self.research.research_topic(user_message)

        # Delete status message
        await status_msg.delete()

        # Update conversation history
        self.conversation_history[user_id].append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history[user_id].append(
            {"role": "assistant", "content": response}
        )

        # Limit history to last 10 messages
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][
                -10:
            ]

        # Send response (no parse_mode to avoid markdown parsing errors)
        await update.message.reply_text(
            response, disable_web_page_preview=True
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
