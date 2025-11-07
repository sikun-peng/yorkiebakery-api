# app/routes/cart.py
from __future__ import annotations

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException
from sqlmodel import Session, select

from app.core.db import engine
from app.core.ddb import add_item, remove_item, get_cart, clear_cart, ensure_table
from app.models.postgres.menu import MenuItem

router = APIRouter(prefix="/cart", tags=["cart"])

CART_COOKIE = "yorkie_cart_id"


def _ensure_cart_id(request: Request) -> str:
    # session middleware is already mounted in the app
    cart_id = request.session.get(CART_COOKIE)
    if not cart_id:
        # use the client host + a random suffix; but simplest is Starlette session ID itself
        import uuid
        cart_id = str(uuid.uuid4())
        request.session[CART_COOKIE] = cart_id
    return cart_id


@router.on_event("startup")
def _startup():
    ensure_table()


@router.get("")
def get_current_cart(request: Request) -> Dict[str, Any]:
    cart_id = _ensure_cart_id(request)
    raw = get_cart(cart_id)

    # hydrate from Postgres for client convenience
    items = raw.get("items", [])
    menu_ids: List[UUID] = [UUID(i["menu_item_id"]) for i in items]

    detailed: List[Dict[str, Any]] = []
    if menu_ids:
        with Session(engine) as s:
            db_items: List[MenuItem] = list(s.exec(select(MenuItem).where(MenuItem.id.in_(menu_ids))))
        lookup = {str(mi.id): mi for mi in db_items}
        for it in items:
            mi = lookup.get(it["menu_item_id"])
            if not mi:
                # skip stale IDs
                continue
            detailed.append({
                "menu_item_id": str(mi.id),
                "title": mi.title,
                "price": float(mi.price or 0.0),
                "quantity": int(it.get("quantity", 0)),
                "image_url": mi.image_url,
            })

    total = sum(x["price"] * x["quantity"] for x in detailed)
    return {"cart_id": raw["cart_id"], "items": detailed, "total": round(total, 2)}


@router.post("/add")
async def add_to_cart(request: Request, payload: Dict[str, str]) -> Dict[str, Any]:
    cart_id = _ensure_cart_id(request)
    menu_item_id = payload.get("menu_item_id")
    if not menu_item_id:
        raise HTTPException(status_code=400, detail="menu_item_id is required")

    # validate item exists and is available
    with Session(engine) as s:
        mi = s.exec(select(MenuItem).where(MenuItem.id == UUID(menu_item_id), MenuItem.is_available == True)).first()
    if not mi:
        raise HTTPException(status_code=404, detail="Menu item not found or unavailable")

    add_item(cart_id, menu_item_id, inc=1)
    return get_current_cart(request)


@router.post("/remove")
async def remove_from_cart(request: Request, payload: Dict[str, str]) -> Dict[str, Any]:
    cart_id = _ensure_cart_id(request)
    menu_item_id = payload.get("menu_item_id")
    if not menu_item_id:
        raise HTTPException(status_code=400, detail="menu_item_id is required")

    remove_item(cart_id, menu_item_id, dec=1)
    return get_current_cart(request)


@router.post("/clear")
async def clear_current_cart(request: Request) -> Dict[str, Any]:
    cart_id = _ensure_cart_id(request)
    clear_cart(cart_id)
    return {"ok": True}