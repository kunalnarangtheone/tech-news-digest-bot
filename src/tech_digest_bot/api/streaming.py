"""Server-Sent Events streaming utilities."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


def format_sse_event(data: dict) -> str:
    """
    Format data as Server-Sent Event.

    Note: EventSourceResponse from sse_starlette automatically adds the "data: " prefix
    and "\n\n" suffix, so we just return the JSON string.

    Args:
        data: Data to send as SSE event

    Returns:
        JSON string (SSE formatting is handled by EventSourceResponse)
    """
    return json.dumps(data)


async def stream_response(
    research_service,
    message: str,
    history: list[dict[str, str]],
    is_new_topic: bool,
) -> AsyncGenerator[str, None]:
    """
    Stream research response as SSE events.

    Args:
        research_service: ResearchService instance
        message: User message
        history: Conversation history
        is_new_topic: Whether this is a new topic (vs follow-up)

    Yields:
        SSE event strings
    """
    try:
        # Send status update
        yield format_sse_event({"type": "status", "content": "🔍 Researching..."})

        # Get response from research service
        if history and not is_new_topic:
            logger.info(f"Answering follow-up question with {len(history)} messages of context")
            response = await research_service.answer_followup(message, history)
        else:
            logger.info(f"Researching new topic: {message[:50]}...")
            response = await research_service.research_topic(message)

        # Stream response word-by-word
        # In the future, this could integrate with Groq's native streaming
        words = response.split()
        for i, word in enumerate(words):
            yield format_sse_event({"type": "token", "content": word + " "})

            # Small delay to simulate streaming (remove when using native Groq streaming)
            if i % 5 == 0:  # Every 5 words
                await asyncio.sleep(0.02)

        # Send completion signal
        yield format_sse_event({"type": "done", "content": ""})

    except Exception as e:
        logger.error(f"Error in stream_response: {e}", exc_info=True)
        yield format_sse_event({
            "type": "error",
            "content": f"Sorry, an error occurred: {str(e)}"
        })
