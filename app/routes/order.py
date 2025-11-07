# app/routes/orders.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.core.db import get_session
from app.models.postgres.order import Order
from app.models.postgres.order_item import OrderItem
from app.models.postgres.menu import MenuItem

router = APIRouter(prefix="/orders", tags=["orders"])


# -------- Create Order --------
@router.post("/", response_model=Order)
def create_order(
    user_id: str,
    items: List[dict],     # list of { menu_item_id, quantity }
    session: Session = Depends(get_session),
):
    if not items:
        raise HTTPException(status_code=400, detail="No items in order.")

    order = Order(user_id=user_id, total=0.0, status="pending")
    session.add(order)
    session.flush()  # gives order.id

    total_cost = 0.0
    order_items = []

    for item in items:
        menu_item = session.get(MenuItem, item["menu_item_id"])
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item['menu_item_id']} not found")

        qty = item.get("quantity", 1)
        cost = menu_item.price * qty
        total_cost += cost

        order_items.append(
            OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                title=menu_item.title,
                unit_price=menu_item.price,
                quantity=qty
            )
        )

    order.total = total_cost
    order.items = order_items

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


# -------- Get Order by ID --------
@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# -------- List Orders --------
@router.get("/", response_model=List[Order])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()


# -------- List Orders by User --------
@router.get("/user/{user_id}", response_model=List[Order])
def list_orders_by_user(user_id: str, session: Session = Depends(get_session)):
    return session.exec(select(Order).where(Order.user_id == user_id)).all()


# -------- Delete Order --------
@router.delete("/{order_id}")
def delete_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"message": "Order deleted"}