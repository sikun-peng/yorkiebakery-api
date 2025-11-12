from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    File,
    UploadFile,
    Form,
    Request,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from sqlalchemy import any_

from app.models.postgres.menu import MenuItem
from app.core.db import get_session
from app.core.security import require_admin
from app.utils.s3_util import upload_file_to_s3

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/menu", tags=["Menu"])

S3_BUCKET_IMAGE = "yorkiebakery-image"

# -------------------------------
# Public menu view (HTML Page)
# -------------------------------
@router.get("/view")
def view_menu_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(MenuItem).where(MenuItem.is_available == True)).all()

    cart = request.session.get("cart", {})
    cart_count = sum(cart.values())

    return templates.TemplateResponse(
        "menu.html",
        {
            "request": request,
            "items": items,
            "cart": cart,
            "cart_count": cart_count,
        },
    )


# -------------------------------
# Create menu item (with image)
# -------------------------------
@router.post("/", response_model=Optional[MenuItem])
def create_menu_item(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    tags: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    user=Depends(require_admin),
):
    # Validate image type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Upload to S3
    image_url = upload_file_to_s3(image, folder="menu", bucket=S3_BUCKET_IMAGE)

    # Create DB record
    item = MenuItem(
        title=title,
        description=description,
        price=float(price),
        tags=[t.strip() for t in tags.split(",")] if tags else [],
        image_url=image_url,
        is_available=is_available,
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    # ✅ Detect if the request came from a browser form
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        # Redirect back to the menu page
        return RedirectResponse(url="/menu/view", status_code=303)

    # Otherwise return JSON (API clients)
    return item


# -------------------------------
# List menu items (API JSON)
# -------------------------------
@router.get("/", response_model=List[MenuItem])
def list_menu_items(
    skip: int = 0,
    limit: int = 20,
    tag: Optional[str] = Query(None),
    session: Session = Depends(get_session),
):
    query = select(MenuItem).where(MenuItem.is_available == True)
    if tag:
        query = query.where(MenuItem.tags.contains([tag]))
    return session.exec(query.offset(skip).limit(limit)).all()


# -------------------------------
# Search menu items (API JSON)
# -------------------------------
@router.get("/search", response_model=List[MenuItem])
def search_menu_items(
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    dish_type: Optional[str] = Query(None),
    dietary: Optional[str] = Query(None),
    flavor: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    query = select(MenuItem).where(MenuItem.is_available == True)

    if q:
        query = query.where(MenuItem.title.ilike(f"%{q}%") | MenuItem.description.ilike(f"%{q}%"))
    if cuisine:
        query = query.where(MenuItem.cuisine == cuisine)
    if dish_type:
        query = query.where(MenuItem.dish_type == dish_type)
    if dietary:
        query = query.where(dietary == any_(MenuItem.dietary_restrictions))
    if flavor:
        query = query.where(flavor == any_(MenuItem.flavor_profile))
    if min_price is not None:
        query = query.where(MenuItem.price >= min_price)
    if max_price is not None:
        query = query.where(MenuItem.price <= max_price)

    return session.exec(query).all()


# -------------------------------
# Admin UI Page
# -------------------------------
@router.get("/new")
def admin_new_menu_page(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse("menu_new.html", {"request": request})


# -------------------------------
# Get item by ID
# -------------------------------
@router.get("/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: UUID, session: Session = Depends(get_session)):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# -------------------------------
# Update menu item
# -------------------------------
@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(
    item_id: UUID,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    user=Depends(require_admin),
):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    if tags is not None:
        item.tags = [t.strip() for t in tags.split(",") if t.strip()]
    if is_available is not None:
        item.is_available = is_available

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        item.image_url = upload_file_to_s3(image, folder="menu", bucket=S3_BUCKET_IMAGE)

    session.commit()
    session.refresh(item)
    return item


# -------------------------------
# Delete menu item
# -------------------------------
@router.delete("/{item_id}")
def delete_menu_item(item_id: UUID, session: Session = Depends(get_session), user=Depends(require_admin)):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"detail": "Item deleted"}