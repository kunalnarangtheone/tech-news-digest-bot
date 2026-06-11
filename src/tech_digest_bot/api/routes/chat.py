"""Chat endpoints for conversational interactions."""

import logging

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from tech_digest_bot.ai.research import ResearchService
from tech_digest_bot.api.models import ChatRequest, ChatResponse
from tech_digest_bot.api.session import SessionStore
from tech_digest_bot.api.streaming import format_sse_event, stream_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global instances (will be injected from main.py)
session_store: SessionStore | None = None
research_service: ResearchService | None = None


def set_dependencies(store: SessionStore, service: ResearchService):
    """Set global dependencies for chat routes."""
    global session_store, research_service
    session_store = store
    research_service = service


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events.

    Args:
        request: Chat request with message and optional session_id

    Returns:
        EventSourceResponse with SSE stream
    """
    if session_store is None or research_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")

    # Get or create session
    session_id = request.session_id
    if session_id:
        metadata = session_store.get_session(session_id)
        if metadata is None:
            logger.warning(f"Session {session_id} not found, creating new session")
            session_id = session_store.create_session()
    else:
        session_id = session_store.create_session()

    # Get conversation history
    history = session_store.get_history(session_id)

    # Detect topic change
    is_new_topic = False
    if history:
        recent_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history[-5:]  # Last 5 messages
        ]
        is_new_topic = await research_service.is_topic_change(
            request.message, recent_messages
        )

        if is_new_topic:
            logger.info(f"Topic change detected in session {session_id}, clearing history")
            session_store.clear_session(session_id)
            history = []

    # Add user message to history
    session_store.add_message(session_id, "user", request.message)

    # Stream response
    async def generate():
        """Generate SSE events for streaming response."""
        full_response = ""

        try:
            # Include session_id in initial event
            yield format_sse_event({
                "type": "session",
                "content": session_id
            })

            # Stream the research response
            async for event in stream_response(
                research_service, request.message, history, is_new_topic
            ):
                # Extract content from token events to build full response
                if '"type": "token"' in event:
                    try:
                        import json
                        data = json.loads(event.replace("data: ", "").strip())
                        full_response += data.get("content", "")
                    except Exception:
                        pass

                yield event

            # Store assistant response
            if full_response.strip():
                session_store.add_message(session_id, "assistant", full_response.strip())

        except Exception as e:
            logger.error(f"Error in generate: {e}", exc_info=True)
            yield format_sse_event({
                "type": "error",
                "content": f"An error occurred: {str(e)}"
            })

    return EventSourceResponse(generate())


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint (fallback).

    Args:
        request: Chat request with message and optional session_id

    Returns:
        Complete chat response
    """
    if session_store is None or research_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")

    # Get or create session
    session_id = request.session_id
    if session_id:
        metadata = session_store.get_session(session_id)
        if metadata is None:
            logger.warning(f"Session {session_id} not found, creating new session")
            session_id = session_store.create_session()
    else:
        session_id = session_store.create_session()

    # Get conversation history
    history = session_store.get_history(session_id)

    # Detect topic change
    is_new_topic = False
    if history:
        recent_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history[-5:]
        ]
        is_new_topic = await research_service.is_topic_change(
            request.message, recent_messages
        )

        if is_new_topic:
            logger.info(f"Topic change detected in session {session_id}, clearing history")
            session_store.clear_session(session_id)
            history = []

    # Add user message
    session_store.add_message(session_id, "user", request.message)

    # Get response
    try:
        if history and not is_new_topic:
            response = await research_service.answer_followup(request.message, history)
        else:
            response = await research_service.research_topic(request.message)

        # Add assistant message
        session_store.add_message(session_id, "assistant", response)

        # Get updated message count
        updated_history = session_store.get_history(session_id)

        return ChatResponse(
            message=response,
            session_id=session_id,
            message_count=len(updated_history),
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
