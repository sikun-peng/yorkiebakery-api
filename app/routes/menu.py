from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.models.postgres.menu import MenuItem
from app.core.db import get_session
from app.core.security import require_admin
from app.utils.s3_util import upload_file_to_s3

router = APIRouter(prefix="/menu", tags=["Menu"])

S3_BUCKET_IMAGE = "yorkiebakery-image"

# -------------------------------
# Create menu item (with image)
# -------------------------------
@router.post("/", response_model=MenuItem)
def create_menu_item(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    is_available: bool = Form(True),
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    user=Depends(require_admin)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    try:
        image_url = upload_file_to_s3(image, folder="menu", bucket=S3_BUCKET_IMAGE)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

    item = MenuItem(
        title=title,
        description=description,
        tags=tag_list,
        image_url=image_url,
        is_available=is_available
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# -------------------------------
# List menu items (with filter)
# -------------------------------
@router.get("/", response_model=List[MenuItem])
def list_menu_items(
    skip: int = 0,
    limit: int = 20,
    tag: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    query = select(MenuItem).where(MenuItem.is_available == True)
    if tag:
        query = query.where(MenuItem.tags.contains([tag]))
    items = session.exec(query.offset(skip).limit(limit)).all()
    return items

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
# Update menu item (optional image upload)
# -------------------------------
@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(
    item_id: UUID,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    is_available: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    user=Depends(require_admin)
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
        try:
            image_url = upload_file_to_s3(image, folder="menu")
            item.image_url = image_url
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# -------------------------------
# Delete menu item
# -------------------------------
@router.delete("/{item_id}")
def delete_menu_item(
    item_id: UUID,
    session: Session = Depends(get_session),
    user=Depends(require_admin)
):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"detail": "Item deleted"}