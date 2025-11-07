# app/models/postgres/order.py
from __future__ import annotations

from typing import List, Optional
from uuid import uuid4, UUID
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class OrderItem(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="order.id", index=True)
    menu_item_id: UUID = Field(foreign_key="menu_item.id", index=True)
    title: str
    unit_price: float
    quantity: int


class Order(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total: float = Field(default=0.0)

    items: List[OrderItem] = Relationship(sa_relationship_kwargs={"cascade": "all, delete-orphan"})