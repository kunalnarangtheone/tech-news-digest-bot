"""Persistent conversation state management using SQLite."""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class ConversationStore:
    """SQLite-based conversation history storage."""

    def __init__(self, db_path: str = "data/conversations.db"):
        """
        Initialize conversation store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._create_tables()

    def _create_tables(self):
        """Create database tables if not exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    user_id INTEGER NOT NULL,
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_timestamp
                ON conversations(user_id, timestamp DESC)
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    user_id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        session_id: Optional[str] = None
    ):
        """
        Add message to conversation history.

        Args:
            user_id: Telegram user ID
            role: Message role (user/assistant)
            content: Message content
            session_id: Optional session identifier
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations (user_id, role, content, session_id)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role, content, session_id),
            )

            # Update session activity
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions
                    (user_id, session_id, last_activity)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, session_id or "default"),
            )

    def get_history(
        self,
        user_id: int,
        limit: int = 10,
        session_id: Optional[str] = None
    ) -> list[dict[str, str]]:
        """
        Get conversation history for user.

        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages
            session_id: Optional session identifier

        Returns:
            List of message dicts with role and content
        """
        with self._get_connection() as conn:
            query = """
                SELECT role, content, timestamp
                FROM conversations
                WHERE user_id = ?
            """
            params = [user_id]

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            # Reverse to chronological order
            return [
                {"role": row["role"], "content": row["content"]}
                for row in reversed(rows)
            ]

    def clear_history(self, user_id: int, session_id: Optional[str] = None):
        """
        Clear conversation history.

        Args:
            user_id: Telegram user ID
            session_id: Optional session identifier
        """
        with self._get_connection() as conn:
            if session_id:
                conn.execute(
                    "DELETE FROM conversations WHERE user_id = ? AND session_id = ?",
                    (user_id, session_id),
                )
            else:
                conn.execute(
                    "DELETE FROM conversations WHERE user_id = ?",
                    (user_id,),
                )

    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Delete conversations older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted messages
        """
        with self._get_connection() as conn:
            cutoff = datetime.now() - timedelta(days=days)

            result = conn.execute(
                "DELETE FROM conversations WHERE timestamp < ?",
                (cutoff,),
            )

            deleted = result.rowcount
            logger.info(f"Cleaned up {deleted} old conversation messages")

            return deleted

    def get_active_users(self, days: int = 7) -> list[int]:
        """
        Get list of active user IDs in last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of user IDs
        """
        with self._get_connection() as conn:
            cutoff = datetime.now() - timedelta(days=days)

            cursor = conn.execute(
                """
                SELECT DISTINCT user_id
                FROM sessions
                WHERE last_activity > ?
                ORDER BY last_activity DESC
                """,
                (cutoff,),
            )

            return [row["user_id"] for row in cursor.fetchall()]
