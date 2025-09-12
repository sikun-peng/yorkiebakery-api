from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    first_name: str
    last_name: str
    password_hash: str
    is_admin: bool = False