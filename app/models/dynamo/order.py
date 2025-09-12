from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    items: List[OrderItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"  # pending | preparing | completed | canceled
    total_price: Optional[float] = None