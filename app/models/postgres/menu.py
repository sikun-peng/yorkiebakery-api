from sqlmodel import SQLModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_item"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: str
    image_url: Optional[str] = None
    origin: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    flavor_profile: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    dietary_restrictions: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    price: Optional[float] = None
    is_available: bool = True