# app/ai/session_manager.py

from sqlmodel import Session, select
from typing import Optional, Dict, List, Any
from uuid import uuid4
from datetime import datetime, timedelta

from app.models.postgres.chat_session import ChatSession
from app.core.db import engine


def get_or_create_session(session_id: Optional[str] = None, user_id: Optional[str] = None) -> ChatSession:
    """
    Get existing session or create a new one.

    Args:
        session_id: Optional session ID. If None, creates a new session.
        user_id: Optional user ID to associate with the session.

    Returns:
        ChatSession object
    """
    with Session(engine) as db:
        if session_id:
            # Try to find existing session
            statement = select(ChatSession).where(ChatSession.session_id == session_id)
            chat_session = db.exec(statement).first()

            if chat_session:
                # Check if expired
                if chat_session.is_expired():
                    # Delete expired session and create new one
                    db.delete(chat_session)
                    db.commit()
                    chat_session = None
                else:
                    # Extend expiration
                    chat_session.expires_at = datetime.utcnow() + timedelta(hours=24)
                    db.add(chat_session)
                    db.commit()
                    db.refresh(chat_session)
                    return chat_session

        # Create new session if not found or expired
        new_session = ChatSession(
            session_id=session_id or str(uuid4()),
            user_id=user_id,
            conversation_history=[],
            preferences={},
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session


def add_message(
    session_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ChatSession:
    """
    Add a message to the conversation history.

    Args:
        session_id: The session ID
        role: "user" or "assistant"
        content: The message content
        metadata: Optional metadata (e.g., items_shown, filters_used)

    Returns:
        Updated ChatSession object
    """
    with Session(engine) as db:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        chat_session = db.exec(statement).first()

        if not chat_session:
            raise ValueError(f"Session {session_id} not found")

        chat_session.add_message(role, content, metadata)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        return chat_session


def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get conversation history for a session.

    Args:
        session_id: The session ID
        limit: Number of recent messages to return

    Returns:
        List of message dictionaries
    """
    with Session(engine) as db:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        chat_session = db.exec(statement).first()

        if not chat_session:
            return []

        return chat_session.get_recent_messages(limit)


def update_preferences(session_id: str, new_preferences: Dict[str, Any]) -> ChatSession:
    """
    Update user preferences for a session.

    Args:
        session_id: The session ID
        new_preferences: Dictionary of preferences to merge

    Returns:
        Updated ChatSession object
    """
    with Session(engine) as db:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        chat_session = db.exec(statement).first()

        if not chat_session:
            raise ValueError(f"Session {session_id} not found")

        chat_session.update_preferences(new_preferences)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        return chat_session


def get_session_preferences(session_id: str) -> Dict[str, Any]:
    """
    Get preferences for a session.

    Args:
        session_id: The session ID

    Returns:
        Dictionary of preferences
    """
    with Session(engine) as db:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        chat_session = db.exec(statement).first()

        if not chat_session:
            return {}

        return chat_session.preferences or {}


def cleanup_expired_sessions() -> int:
    """
    Delete all expired sessions.

    Returns:
        Number of sessions deleted
    """
    with Session(engine) as db:
        statement = select(ChatSession).where(ChatSession.expires_at < datetime.utcnow())
        expired_sessions = db.exec(statement).all()

        count = len(expired_sessions)
        for session in expired_sessions:
            db.delete(session)

        db.commit()
        return count
