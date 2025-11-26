from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime

from app.core.db import engine
from app.models.postgres.menu import MenuItem
from app.models.postgres.order import Order
from app.models.postgres.order_item import OrderItem
from app.models.postgres.user import User
from app.core.send_email import (
    send_order_confirmation_email,
    send_owner_new_order_email
)

router = APIRouter(prefix="/cart", tags=["Cart"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------
# Helper: get cart from session
# ---------------------------------------------
def _get_cart(request: Request):
    return request.session.setdefault("cart", {})


# ---------------------------------------------
# Helper: verify login & return logged-in user id
# ---------------------------------------------
def require_login(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user.get("id")  # user["id"] stored from /auth/login_form


# ---------------------------------------------
# CART PAGE
# ---------------------------------------------
@router.get("/view")
def view_cart_page(request: Request):
    cart = _get_cart(request)
    item_ids = list(cart.keys())
    items = []

    if item_ids:
        with Session(engine) as session:
            results = session.exec(
                select(MenuItem).where(MenuItem.id.in_(item_ids))
            ).all()

            for item in results:
                qty = cart.get(str(item.id), 0)
                items.append({
                    "id": item.id,
                    "title": item.title,
                    "price": item.price,
                    "quantity": qty,
                    "subtotal": item.price * qty,
                })

    original_total = sum(i["subtotal"] for i in items)
    total = 0  # 100% off promotion
    cart_count = sum(cart.values())

    return templates.TemplateResponse("cart.html", {
        "request": request,
        "items": items,
        "original_total": original_total,
        "total": total,
        "cart": cart,
        "cart_count": cart_count,
    })


# ---------------------------------------------
# ADD ITEM (AJAX)
# ---------------------------------------------
@router.post("/add")
async def add_item_json(request: Request):
    data = await request.json()
    menu_item_id = str(data["menu_item_id"])

    cart = _get_cart(request)
    cart[menu_item_id] = cart.get(menu_item_id, 0) + 1
    request.session["cart"] = cart

    return {
        "ok": True,
        "cart_count": sum(cart.values()),
        "item_count": cart[menu_item_id]
    }


# ---------------------------------------------
# ADD ITEM (+)
# ---------------------------------------------
@router.post("/add/{menu_item_id}")
def add_item_button(menu_item_id: str, request: Request):
    cart = _get_cart(request)
    cart[menu_item_id] = cart.get(menu_item_id, 0) + 1
    request.session["cart"] = cart
    referer = request.headers.get("referer", "/menu/view")
    return RedirectResponse(url=referer, status_code=303)


# ---------------------------------------------
# REMOVE ITEM (AJAX)
# ---------------------------------------------
@router.post("/remove")
async def remove_item_json(request: Request):
    data = await request.json()
    menu_item_id = str(data["menu_item_id"])

    cart = _get_cart(request)
    if menu_item_id in cart:
        cart[menu_item_id] -= 1
        if cart[menu_item_id] <= 0:
            del cart[menu_item_id]
    request.session["cart"] = cart

    return {
        "ok": True,
        "cart_count": sum(cart.values()),
        "item_count": cart.get(menu_item_id, 0)
    }


# ---------------------------------------------
# REMOVE ITEM (−)
# ---------------------------------------------
@router.post("/remove/{menu_item_id}")
def remove_item_button(menu_item_id: str, request: Request):
    cart = _get_cart(request)
    if menu_item_id in cart:
        cart[menu_item_id] -= 1
        if cart[menu_item_id] <= 0:
            del cart[menu_item_id]
    request.session["cart"] = cart
    referer = request.headers.get("referer", "/menu/view")
    return RedirectResponse(url=referer, status_code=303)


# ---------------------------------------------
# CHECKOUT PAGE (LOGIN REQUIRED)
# ---------------------------------------------
@router.get("/checkout")
def checkout_page(request: Request):
    # Check login
    user_id = require_login(request)
    if not user_id:
        return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

    cart = _get_cart(request)
    if not cart:
        return RedirectResponse("/menu/view", status_code=303)

    with Session(engine) as session:
        items = session.exec(
            select(MenuItem).where(MenuItem.id.in_(cart.keys()))
        ).all()

        detailed_cart = [
            {"title": i.title, "price": i.price, "qty": cart.get(str(i.id), 0)}
            for i in items
        ]

    original_total = sum(i["price"] * i["qty"] for i in detailed_cart)
    total = 0  # 100% off promotion

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "cart": detailed_cart,
        "original_total": original_total,
        "total": total,
        "discount_percent": 100,
    })


# ---------------------------------------------
# PROCESS CHECKOUT (FIXED VERSION)
# ---------------------------------------------
@router.post("/checkout")
def process_checkout(
        request: Request,
        address: str = Form(...)
):
    # Must be logged in
    user_id = require_login(request)
    if not user_id:
        return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

    cart = _get_cart(request)
    if not cart:
        return RedirectResponse("/menu/view", status_code=303)

    # Store user info before session closes
    user_email = None
    user_name = None

    with Session(engine) as session:

        user = session.get(User, user_id)
        if not user:
            return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

        # Store user info while session is active
        user_email = user.email
        user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        items = session.exec(
            select(MenuItem).where(MenuItem.id.in_(cart.keys()))
        ).all()

        cart_items = []
        original_total = 0
        total = 0  # after 100% discount

        for item in items:
            qty = cart.get(str(item.id), 0)
            subtotal = item.price * qty
            original_total += subtotal

            cart_items.append({
                "title": item.title,
                "qty": qty,
                "price": item.price,
                "subtotal": subtotal,
                "menu_item_id": str(item.id)
            })

        # Create order
        order = Order(
            id=uuid4(),
            user_id=user_id,
            total=total,
            status="confirmed",
            created_at=datetime.utcnow()
        )

        session.add(order)
        session.commit()  # Commit to get order ID
        session.refresh(order)

        # Create order items individually (FIXED - no relationship assignment)
        for ci in cart_items:
            order_item = OrderItem(
                id=uuid4(),
                order_id=order.id,
                menu_item_id=ci["menu_item_id"],
                title=ci["title"],
                unit_price=ci["price"],
                quantity=ci["qty"]
            )
            session.add(order_item)

        # Commit all order items
        session.commit()

    # Send emails (using stored user info)
    try:
        send_order_confirmation_email(
            email=user_email,
            order_items=cart_items,
            total=total
        )
        send_owner_new_order_email(
            order_items=cart_items,
            total=total,
            customer_email=user_email
        )
    except Exception as e:
        print("⚠️ Email send error:", e)

    # Clear cart
    request.session["cart"] = {}

    return templates.TemplateResponse("confirm.html", {
        "request": request,
        "cart": cart_items,
        "original_total": original_total,
        "total": total,
        "discount_percent": 100,
        "email": user_email,
        "name": user_name
    })
