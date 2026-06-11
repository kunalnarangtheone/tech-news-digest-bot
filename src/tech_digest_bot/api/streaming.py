"""Server-Sent Events streaming utilities."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

logger = logging.getLogger(__name__)

# Map LangGraph node names to user-friendly status messages
NODE_STATUS_MESSAGES = {
    "classifier": "🔍 Analyzing question...",
    "fast_path": "⚡ Quick lookup...",
    "planner": "📋 Planning research strategy...",
    "search_agents": "🌐 Searching the web...",
    "synthesizer": "✍️ Synthesizing findings...",
    "critic": "🔎 Verifying quality...",
    "advocate_a": "⚖️ Building case (advocate A)...",
    "advocate_b": "⚖️ Building case (advocate B)...",
    "judge": "⚖️ Judging arguments...",
    "followup": "💡 Generating follow-up questions...",
}


def format_sse_event(data: dict[str, Any]) -> str:
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
    research_service: Any,
    message: str,
    history: list[dict[str, str]],
    is_new_topic: bool,
) -> AsyncGenerator[str]:
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
        # Send initial status
        yield format_sse_event({"type": "status", "content": "🔍 Starting research..."})

        # Check if using LangGraph streaming
        if research_service.use_graph and research_service.qa_graph:
            # Stream LangGraph events
            logger.info("Using LangGraph streaming")
            async for event_type, data in research_service.research_topic_with_graph_stream(message):
                if event_type == "node_start":
                    node = data["node"]
                    status = NODE_STATUS_MESSAGES.get(node, f"Processing {node}...")
                    yield format_sse_event({"type": "status", "content": status})

                elif event_type == "node_end":
                    # Could emit intermediate results here if needed
                    logger.debug(f"Node {data['node']} completed")

                elif event_type == "complete":
                    # Stream the final answer
                    answer = data.get("answer", "")
                    if answer:
                        # Stream in small chunks while preserving whitespace and newlines
                        # This is critical for markdown rendering
                        chunk_size = 50  # characters per chunk
                        for i in range(0, len(answer), chunk_size):
                            chunk = answer[i:i + chunk_size]
                            yield format_sse_event({"type": "token", "content": chunk})
                            if i % 500 == 0:  # Small delay every ~500 chars
                                await asyncio.sleep(0.01)

                    # Send completion with metadata
                    yield format_sse_event({
                        "type": "metadata",
                        "content": {
                            "citations": data.get("citations", []),
                            "confidence": data.get("confidence", 0.0),
                            "debate_flag": data.get("debate_flag", False),
                            "followups": data.get("followups", []),
                        }
                    })

        else:
            # Fallback to non-graph streaming
            if history and not is_new_topic:
                logger.info(f"Answering follow-up question with {len(history)} messages of context")
                response = await research_service.answer_followup(message, history)
            else:
                logger.info(f"Researching new topic: {message[:50]}...")
                response = await research_service.research_topic(message)

            # Stream in small chunks while preserving whitespace and newlines
            # This is critical for markdown rendering
            chunk_size = 50  # characters per chunk
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                yield format_sse_event({"type": "token", "content": chunk})
                if i % 500 == 0:  # Small delay every ~500 chars
                    await asyncio.sleep(0.01)

        # Send completion signal
        yield format_sse_event({"type": "done", "content": ""})

    except Exception as e:
        logger.error(f"Error in stream_response: {e}", exc_info=True)
        yield format_sse_event({
            "type": "error",
            "content": f"Sorry, an error occurred: {str(e)}"
        })
