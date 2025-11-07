from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.db import get_session
from app.models.postgres.order import Order

router = APIRouter(prefix="/orders", tags=["orders"])

# Create Order
@router.post("/", response_model=Order)
def create_order(order: Order, session: Session = Depends(get_session)):
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

# Get Order by ID
@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# List all Orders
@router.get("/", response_model=List[Order])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()

# Get Orders by user_id
@router.get("/user/{user_id}", response_model=List[Order])
def list_orders_by_user(user_id: str, session: Session = Depends(get_session)):
    return session.exec(select(Order).where(Order.user_id == user_id)).all()

# Delete Order
@router.delete("/{order_id}")
def delete_order(order_id: str, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"message": "Order deleted"}