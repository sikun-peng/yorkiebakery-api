from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime

from app.core.db import engine
from app.core.logger import get_logger

logger = get_logger(__name__)
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
# Helper: user address defaults
# ---------------------------------------------
def _address_defaults(user: User) -> dict:
    return {
        "address_line1": user.address_line1 or "",
        "address_line2": user.address_line2 or "",
        "city": user.city or "",
        "state": user.state or "",
        "postal_code": user.postal_code or "",
        "country": user.country or "",
        "default_phone": user.default_phone or "",
    }


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
        user = session.get(User, user_id)
        contact_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip() if user else ""
        contact_email = user.email if user else ""
        contact_phone = user.default_phone if user else ""
        address_defaults = _address_defaults(user) if user else {
            "address_line1": "",
            "address_line2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "country": "",
            "default_phone": "",
        }

    original_total = sum(i["price"] * i["qty"] for i in detailed_cart)
    total = 0  # 100% off promotion

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "cart": detailed_cart,
        "original_total": original_total,
        "total": total,
        "discount_percent": 100,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "address_defaults": address_defaults,
    })


# ---------------------------------------------
# PROCESS CHECKOUT (FIXED VERSION)
# ---------------------------------------------
@router.post("/checkout")
def process_checkout(
        request: Request,
        name: str = Form(None),
        email: str = Form(None),
        phone: str = Form(None),
        address_line1: str = Form(...),
        address_line2: str = Form(None),
        city: str = Form(...),
        state: str = Form(...),
        postal_code: str = Form(...),
        country: str = Form(...),
        delivery_notes: str = Form(None)
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
    user_phone = phone or ""
    user_address = ""
    notes = delivery_notes

    with Session(engine) as session:

        user = session.get(User, user_id)
        if not user:
            return RedirectResponse("/auth/login?redirect_url=/cart/checkout", status_code=303)

        def clean(value):
            if value is None:
                return None
            return value.strip() or None

        cleaned_address = {
            "address_line1": clean(address_line1),
            "address_line2": clean(address_line2),
            "city": clean(city),
            "state": clean(state),
            "postal_code": clean(postal_code),
            "country": clean(country),
        }
        phone_clean = clean(phone)

        city_state = ", ".join(filter(None, [cleaned_address["city"], cleaned_address["state"]]))
        city_state_postal = " ".join(filter(None, [city_state, cleaned_address["postal_code"]]))
        address_parts = [
            cleaned_address["address_line1"],
            cleaned_address["address_line2"],
            city_state_postal,
            cleaned_address["country"],
        ]
        user_address = ", ".join([part for part in address_parts if part])

        # Store user info while session is active
        user_email = email or user.email
        user_name = name or f"{user.first_name or ''} {user.last_name or ''}".strip()
        user_phone = phone_clean or user.default_phone or ""

        # Update stored defaults to match the last used delivery info
        user.address_line1 = cleaned_address["address_line1"]
        user.address_line2 = cleaned_address["address_line2"]
        user.city = cleaned_address["city"]
        user.state = cleaned_address["state"]
        user.postal_code = cleaned_address["postal_code"]
        user.country = cleaned_address["country"]
        if phone_clean is not None:
            user.default_phone = phone_clean
        session.add(user)

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
        order_id = str(order.id)

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

    # Build order link for emails
    base_url = str(request.base_url).rstrip("/")
    order_url = f"{base_url}/orders/{order_id}/detail"

    # Send emails (using stored user info)
    try:
        send_order_confirmation_email(
            email=user_email,
            order_items=cart_items,
            total=total,
            customer_name=user_name,
            delivery_address=user_address,
            phone=user_phone,
            delivery_notes=notes,
            order_id=order_id,
            order_url=order_url,
            discount_percent=100,
            original_total=original_total
        )
        send_owner_new_order_email(
            order_items=cart_items,
            total=total,
            customer_email=user_email,
            customer_name=user_name,
            delivery_address=user_address,
            phone=user_phone,
            delivery_notes=notes,
            order_id=order_id,
            order_url=order_url,
            discount_percent=100,
            original_total=original_total
        )
    except Exception as e:
        logger.warning(f"Email send error: {e}")

    # Clear cart
    request.session["cart"] = {}

    return templates.TemplateResponse("confirm.html", {
        "request": request,
        "cart": cart_items,
        "original_total": original_total,
        "total": total,
        "discount_percent": 100,
        "email": user_email,
        "name": user_name,
        "address": user_address,
        "phone": user_phone,
        "notes": notes
    })
