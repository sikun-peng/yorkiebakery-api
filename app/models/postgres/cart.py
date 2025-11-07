from typing import List
from sqlmodel import SQLModel, Field, Relationship
import uuid

class Cart(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)

    items: List["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cart_id: uuid.UUID = Field(foreign_key="cart.id")
    menu_item_id: uuid.UUID = Field(foreign_key="menu_item.id")
    quantity: int = Field(default=1)

    cart: Cart = Relationship(back_populates="items")