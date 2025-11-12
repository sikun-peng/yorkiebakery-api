from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    __tablename__ = "user_account"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = None