from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Column, Text

class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_token"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user_account.id")
    token: str = Field(sa_column=Column(Text, nullable=False, index=True))
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)