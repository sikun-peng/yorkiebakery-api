from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

class Review(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(nullable=False)
    menu_item_id: UUID = Field(nullable=False)
    rating: int = Field(ge=1, le=5, nullable=False)
    comment: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)