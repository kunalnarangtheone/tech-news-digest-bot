"""Session management endpoints."""

from fastapi import APIRouter, HTTPException

from tech_digest_bot.api.models import NewSessionRequest, SessionResponse
from tech_digest_bot.api.session import SessionStore

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Global session store (will be initialized in main.py)
session_store: SessionStore | None = None


def set_session_store(store: SessionStore):
    """Set the global session store instance."""
    global session_store
    session_store = store


@router.post("/", response_model=SessionResponse)
async def create_session(request: NewSessionRequest) -> SessionResponse:
    """
    Create a new conversation session.

    Args:
        request: New session request with optional user_id

    Returns:
        Session metadata including session_id
    """
    if session_store is None:
        raise HTTPException(status_code=500, detail="Session store not initialized")

    session_id = session_store.create_session(user_id=request.user_id)
    metadata = session_store.get_session(session_id)

    if metadata is None:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return SessionResponse(**metadata)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Get session metadata.

    Args:
        session_id: Session identifier

    Returns:
        Session metadata
    """
    if session_store is None:
        raise HTTPException(status_code=500, detail="Session store not initialized")

    metadata = session_store.get_session(session_id)

    if metadata is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(**metadata)


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    """
    Delete a session.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if session_store is None:
        raise HTTPException(status_code=500, detail="Session store not initialized")

    metadata = session_store.get_session(session_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session_store.delete_session(session_id)

    return {"message": "Session deleted successfully"}


@router.post("/{session_id}/clear")
async def clear_session(session_id: str) -> dict:
    """
    Clear session history but keep session alive.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if session_store is None:
        raise HTTPException(status_code=500, detail="Session store not initialized")

    metadata = session_store.get_session(session_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session_store.clear_session(session_id)

    return {"message": "Session cleared successfully"}
