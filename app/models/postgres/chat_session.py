from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: str = Field(index=True, unique=True, nullable=False)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user_account.id")
    conversation_history: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history and keep only last 10 turns (20 messages)"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata

        # Add new message
        if not self.conversation_history:
            self.conversation_history = []
        self.conversation_history.append(message)

        # Keep only last 20 messages (10 turns)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        self.last_message_at = datetime.utcnow()

    def update_preferences(self, new_prefs: Dict[str, Any]):
        """Merge new preferences with existing ones"""
        if not self.preferences:
            self.preferences = {}

        for key, value in new_prefs.items():
            if key in self.preferences:
                # Merge lists
                if isinstance(value, list) and isinstance(self.preferences[key], list):
                    # Add unique values only
                    existing = set(self.preferences[key])
                    for item in value:
                        if item not in existing:
                            self.preferences[key].append(item)
                else:
                    self.preferences[key] = value
            else:
                self.preferences[key] = value

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation messages (returns last N messages)"""
        if not self.conversation_history:
            return []
        return self.conversation_history[-limit:]

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
