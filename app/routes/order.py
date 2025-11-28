from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from uuid import UUID
from sqlmodel import Session, select
from typing import List, Dict, Any

from app.core.db import get_session
from app.models.postgres.order import Order
from app.models.postgres.order_item import OrderItem
from app.models.postgres.menu import MenuItem
from app.models.postgres.user import User

router = APIRouter(prefix="/order", tags=["Orders"])
templates = Jinja2Templates(directory="app/templates")


# -----------------------------------------------
# UI: View all orders for the logged-in user - FIXED VERSION
# /orders/view  ← THIS MUST COME BEFORE {order_id}
# -----------------------------------------------
@router.get("/view")
def orders_view_page(request: Request, session: Session = Depends(get_session)):
    user_session = request.session.get("user")
    if not user_session:
        # No logged in session → redirect to login
        return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

    user_id = user_session["id"]

    # Fetch user's orders
    orders = session.exec(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    ).all()

    # Manually fetch items for each order
    orders_with_items = []
    for order in orders:
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()

        # Convert UUIDs to strings for template compatibility
        order_dict = {
            "id": str(order.id),  # Convert UUID to string
            "user_id": str(order.user_id),
            "status": order.status,
            "created_at": order.created_at,
            "total": order.total
        }

        # Convert order item UUIDs to strings
        items_list = []
        for item in order_items:
            item_dict = {
                "id": str(item.id),
                "order_id": str(item.order_id),
                "menu_item_id": str(item.menu_item_id),
                "title": item.title,
                "unit_price": item.unit_price,
                "quantity": item.quantity
            }
            items_list.append(item_dict)

        orders_with_items.append({
            "order": order_dict,  # Use the converted dictionary
            "items": items_list  # Use the converted list
        })

    return templates.TemplateResponse(
        "order.html",
        {
            "request": request,
            "orders_with_items": orders_with_items,
            "user": user_session,
        }
    )


# -----------------------------------------------
# Create Order (API) - FIXED VERSION
# -----------------------------------------------
@router.post("/", response_model=Order)
def create_order(
        user_id: UUID,
        items: List[dict],
        session: Session = Depends(get_session),
):
    if not items:
        raise HTTPException(status_code=400, detail="No items in order.")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create order first
    order = Order(user_id=str(user_id), total=0.0, status="pending")
    session.add(order)
    session.commit()  # Commit to get order.id
    session.refresh(order)

    total_cost = 0.0

    # Create order items individually (FIXED - no relationship assignment)
    for item in items:
        menu_item_id = item.get("menu_item_id")
        qty = item.get("quantity", 1)

        menu_item = session.get(MenuItem, menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item not found: {menu_item_id}")

        cost = menu_item.price * qty
        total_cost += cost

        # Create and add each order item
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            title=menu_item.title,
            unit_price=menu_item.price,
            quantity=qty
        )
        session.add(order_item)

    # Update order total
    order.total = total_cost
    session.add(order)
    session.commit()
    session.refresh(order)

    return order


# -----------------------------------------------
# Get order by ID with items (FIXED)
# /orders/{order_id}
# -----------------------------------------------
@router.get("/{order_id}")
def get_order(order_id: UUID, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get order items separately since relationship might not work
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    return {
        "order": order,
        "items": order_items
    }


# -----------------------------------------------
# Order Detail Page - FIXED: Convert UUIDs for template
# -----------------------------------------------
@router.get("/{order_id}/detail")
def order_detail_page(order_id: UUID, request: Request, session: Session = Depends(get_session)):
    user_session = request.session.get("user")
    if not user_session:
        return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify order belongs to user
    if str(order.user_id) != user_session["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get order items manually
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    # Convert UUIDs to strings for template
    order_dict = {
        "id": str(order.id),
        "user_id": str(order.user_id),
        "status": order.status,
        "created_at": order.created_at,
        "total": order.total
    }

    # Convert order items
    items_list = []
    for item in order_items:
        item_dict = {
            "id": str(item.id),
            "order_id": str(item.order_id),
            "menu_item_id": str(item.menu_item_id),
            "title": item.title,
            "unit_price": item.unit_price,
            "quantity": item.quantity
        }
        items_list.append(item_dict)

    return templates.TemplateResponse(
        "order_detail.html",
        {
            "request": request,
            "order": order_dict,  # Use converted order
            "items": items_list,  # Use converted items
            "user": user_session,
        }
    )


# -----------------------------------------------
# List orders for a specific user
# (MUST be above single order lookup)
# -----------------------------------------------
@router.get("/user/{user_id}", response_model=List[Order])
def list_orders_by_user(user_id: UUID, session: Session = Depends(get_session)):
    return session.exec(
        select(Order).where(Order.user_id == str(user_id))
    ).all()


# -----------------------------------------------
# List ALL orders (admin)
# -----------------------------------------------
@router.get("/", response_model=List[Order])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()


# -----------------------------------------------
# Update order status (admin)
# -----------------------------------------------
@router.put("/{order_id}/status")
def update_order_status(order_id: UUID, payload: Dict[str, Any] = Body(...), session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    new_status = payload.get("status")
    if new_status:
        order.status = new_status
        session.add(order)
        session.commit()
    return {"status": order.status}


# -----------------------------------------------
# Cancel order
# -----------------------------------------------
@router.post("/{order_id}/cancel")
def cancel_order(order_id: UUID, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "canceled"
    session.add(order)
    session.commit()
    return {"status": "canceled"}


# -----------------------------------------------
# Delete order with cascade handling
# -----------------------------------------------
@router.delete("/{order_id}")
def delete_order(order_id: UUID, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # First delete order items (if cascade isn't working)
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    for item in order_items:
        session.delete(item)

    # Then delete the order
    session.delete(order)
    session.commit()
    return {"message": "Order deleted"}
