# app/routes/cart.py
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.core.db import engine
from app.models.postgres.menu import MenuItem

router = APIRouter(prefix="/cart", tags=["Cart"])
templates = Jinja2Templates(directory="app/templates")


def _get_cart(request: Request):
    """
    Ensure cart exists in session and return it.
    Structure: {"menu_item_id": quantity}
    """
    return request.session.setdefault("cart", {})


# -------------------
# CART PAGE (HTML)
# -------------------
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

    total = sum(i["subtotal"] for i in items)
    cart_count = sum(cart.values())

    return templates.TemplateResponse("cart.html", {
        "request": request,
        "items": items,
        "total": total,
        "cart": cart,
        "cart_count": cart_count,
    })


# -------------------
# ADD ITEM (AJAX)
# -------------------
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


# -------------------
# PLUS BUTTON (+) — FORM POST
# -------------------
@router.post("/add/{menu_item_id}")
def add_item_button(menu_item_id: str, request: Request):
    cart = _get_cart(request)
    cart[menu_item_id] = cart.get(menu_item_id, 0) + 1
    request.session["cart"] = cart
    return RedirectResponse(url="/menu/view", status_code=303)


# -------------------
# MINUS BUTTON (−) — FORM POST
# -------------------
@router.post("/remove/{menu_item_id}")
def remove_item_button(menu_item_id: str, request: Request):
    cart = _get_cart(request)
    if menu_item_id in cart:
        cart[menu_item_id] -= 1
        if cart[menu_item_id] <= 0:
            del cart[menu_item_id]
    request.session["cart"] = cart
    return RedirectResponse(url="/menu/view", status_code=303)