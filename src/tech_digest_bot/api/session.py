"""Session management for web API."""

import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionStore:
    """Manages conversation sessions for web API."""

    def __init__(self, use_sqlite: bool = True, ttl_hours: int = 24):
        """
        Initialize session store.

        Args:
            use_sqlite: Whether to use SQLite for persistence
            ttl_hours: Session time-to-live in hours
        """
        # In-memory cache for fast access
        self._sessions: dict[str, list[dict[str, str]]] = {}
        self._session_metadata: dict[str, dict] = {}
        self.ttl_hours = ttl_hours

        # Optional SQLite persistence
        self.use_sqlite = use_sqlite
        self.db_path = Path("data/web_conversations.db")
        if use_sqlite:
            self._init_db()

    def _init_db(self):
        """Initialize SQLite database for session persistence."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def create_session(self, user_id: str | None = None) -> str:
        """
        Create a new session.

        Args:
            user_id: Optional user identifier

        Returns:
            New session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        self._session_metadata[session_id] = {
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "user_id": user_id,
        }

        logger.info(f"Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        """
        Get session metadata.

        Args:
            session_id: Session identifier

        Returns:
            Session metadata or None if not found
        """
        if session_id not in self._session_metadata:
            return None

        metadata = self._session_metadata[session_id].copy()
        metadata["session_id"] = session_id
        metadata["message_count"] = len(self._sessions.get(session_id, []))
        return metadata

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to session history.

        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
        """
        if session_id not in self._sessions:
            logger.warning(f"Session {session_id} not found, creating it")
            self.create_session()

        # Add to in-memory cache
        self._sessions[session_id].append({"role": role, "content": content})

        # Limit to last 10 messages for context window management
        if len(self._sessions[session_id]) > 10:
            self._sessions[session_id] = self._sessions[session_id][-10:]

        # Update last activity
        if session_id in self._session_metadata:
            self._session_metadata[session_id]["last_activity"] = datetime.now()

        # Persist to SQLite if enabled
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )
            conn.commit()
            conn.close()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages with role and content
        """
        if session_id not in self._sessions:
            # Try to load from SQLite if enabled
            if self.use_sqlite:
                user_id_hash = hash(session_id) % (10**9)
                history = self.store.get_history(
                    user_id=user_id_hash, limit=10, session_id=session_id
                )
                if history:
                    self._sessions[session_id] = history
                    return history

            return []

        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        """
        Clear session history but keep session alive.

        Args:
            session_id: Session identifier
        """
        if session_id in self._sessions:
            self._sessions[session_id] = []

            if self.use_sqlite:
                user_id_hash = hash(session_id) % (10**9)
                self.store.clear_history(user_id=user_id_hash, session_id=session_id)

            logger.info(f"Cleared session: {session_id}")

    def delete_session(self, session_id: str):
        """
        Delete a session completely.

        Args:
            session_id: Session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

        if session_id in self._session_metadata:
            del self._session_metadata[session_id]

        if self.use_sqlite:
            user_id_hash = hash(session_id) % (10**9)
            self.store.clear_history(user_id=user_id_hash, session_id=session_id)

        logger.info(f"Deleted session: {session_id}")

    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessions older than TTL.

        Returns:
            Number of sessions removed
        """
        cutoff = datetime.now() - timedelta(hours=self.ttl_hours)
        expired_sessions = [
            session_id
            for session_id, metadata in self._session_metadata.items()
            if metadata["last_activity"] < cutoff
        ]

        for session_id in expired_sessions:
            self.delete_session(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def get_all_sessions(self) -> list[dict]:
        """
        Get all active sessions.

        Returns:
            List of session metadata
        """
        return [
            {
                "session_id": session_id,
                **metadata,
                "message_count": len(self._sessions.get(session_id, [])),
            }
            for session_id, metadata in self._session_metadata.items()
        ]
