from __future__ import annotations
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class OrderItem(SQLModel, table=True):
    __tablename__ = "orderitem"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="order.id", index=True)
    menu_item_id: UUID = Field(foreign_key="menu_item.id", index=True)
    title: str
    unit_price: float
    quantity: int