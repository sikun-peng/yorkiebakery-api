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
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import any_
from collections import defaultdict

from app.core.logger import get_logger

logger = get_logger(__name__)

from app.models.postgres.menu import MenuItem
from app.models.postgres.review import Review
from app.models.postgres.user import User
from app.core.db import get_session
from app.core.security import require_admin
from app.core.cart_utils import get_cart_count
from app.core.markdown import render_markdown
from app.utils.s3_util import upload_file_to_s3
import os

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown

router = APIRouter(prefix="/menu", tags=["Menu"])

S3_BUCKET_IMAGE = os.getenv("S3_BUCKET_IMAGE", "yorkiebakery-image")
CATEGORY_DISPLAY_ORDER = [
    "pastry",
    "dessert",
    "appetizer",
    "entree",
    "rice_and_noodles",
    "drink",
    "soup",
]


def _normalize_list_item(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _parse_csv_or_list(value: Optional[Union[str, List[str]]]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        parsed: List[str] = []
        for entry in value:
            parsed.extend(
                normalized
                for part in entry.split(",")
                if (normalized := _normalize_list_item(part))
            )
        return parsed
    return [
        normalized
        for part in value.split(",")
        if (normalized := _normalize_list_item(part))
    ]


def _item_has_chef_special_tag(item: MenuItem) -> bool:
    return bool(item.tags and any(tag.lower() == "chef special" for tag in item.tags))


def _build_review_stats(reviews: List[Review]) -> dict:
    review_stats = defaultdict(lambda: {"count": 0, "avg_rating": 0})
    rating_totals = defaultdict(int)

    for review in reviews:
        key = str(review.menu_item_id)
        review_stats[key]["count"] += 1
        rating_totals[key] += review.rating

    for key, stats in review_stats.items():
        if stats["count"] > 0:
            stats["avg_rating"] = round(rating_totals[key] / stats["count"], 1)

    return dict(review_stats)


def _menu_sort_key(item: MenuItem, review_stats: dict) -> tuple:
    stats = review_stats.get(str(item.id), {"count": 0, "avg_rating": 0})
    category = item.category or "default"
    category_rank = (
        CATEGORY_DISPLAY_ORDER.index(category)
        if category in CATEGORY_DISPLAY_ORDER
        else len(CATEGORY_DISPLAY_ORDER)
    )
    return (
        category_rank,
        0 if _item_has_chef_special_tag(item) else 1,
        -stats["count"],
        -stats["avg_rating"],
        (item.title or "").lower(),
    )


# -------------------------------
# Public menu view (HTML Page)
# -------------------------------
@router.get("/view")
def view_menu_page(
        request: Request,
        session: Session = Depends(get_session),
        dietary: List[str] = Query(None)
):
    try:
        all_items = session.exec(select(MenuItem).where(MenuItem.is_available == True)).all()
        all_reviews = session.exec(select(Review)).all()
        review_stats = _build_review_stats(all_reviews)

        if dietary:
            filtered_items = []
            for item in all_items:
                if item.dietary_features and all(diet in item.dietary_features for diet in dietary):
                    filtered_items.append(item)
            items = filtered_items
        else:
            items = all_items

        items = sorted(items, key=lambda item: _menu_sort_key(item, review_stats))
        for item in items:
            review_stats.setdefault(str(item.id), {"count": 0, "avg_rating": 0})

        cart = request.session.get("cart", {})
        cart_count = sum(cart.values())

        return templates.TemplateResponse(
            request,
            "menu.html",
            {
                "items": items,
                "cart": cart,
                "cart_count": cart_count,
                "review_stats": review_stats,
            },
        )
    except Exception as e:
        logger.error(f"Error in view_menu_page: {e}", exc_info=True)
        # Return empty response on error
        return templates.TemplateResponse(
            request,
            "menu.html",
            {
                "items": [],
                "cart": {},
                "cart_count": 0,
                "review_stats": {},
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
    category: Optional[str] = Form(None),
    origin: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    flavor_profiles: Optional[str] = Form(None),
    dietary_features: Optional[List[str]] = Form(None),
    recipe: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    session: Session = Depends(get_session),
    user=Depends(require_admin),
):
    # Normalize uploaded files (support single or multi)
    uploaded_files: List[UploadFile] = []
    if images:
        uploaded_files.extend(images)
    if image:
        uploaded_files.append(image)

    # Filter out empty file inputs (common when multiple fields exist)
    uploaded_files = [f for f in uploaded_files if f and f.filename]

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="At least one image is required")

    def is_image_file(upload: UploadFile) -> bool:
        if upload.content_type and upload.content_type.startswith("image/"):
            return True
        filename = (upload.filename or "").lower()
        return filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic"))

    uploaded_urls: List[str] = []
    for f in uploaded_files:
        if not is_image_file(f):
            logger.warning(
                "Rejected non-image upload for menu item",
                extra={"upload_filename": f.filename, "upload_content_type": f.content_type},
            )
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        uploaded_urls.append(upload_file_to_s3(f, folder="menu", bucket=S3_BUCKET_IMAGE))

    image_url = uploaded_urls[0]
    gallery_urls = uploaded_urls[1:] if len(uploaded_urls) > 1 else []

    item = MenuItem(
        title=title,
        description=description,
        price=float(price),
        category=category,
        origin=origin,
        tags=_parse_csv_or_list(tags),
        flavor_profiles=_parse_csv_or_list(flavor_profiles),
        dietary_features=_parse_csv_or_list(dietary_features),
        recipe=recipe,
        image_url=image_url,
        gallery_urls=gallery_urls,
        is_available=is_available,
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    # Browser redirect
    if "multipart/form-data" in request.headers.get("content-type", ""):
        return RedirectResponse(url="/menu/view", status_code=303)

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
# Search menu items
# -------------------------------
@router.get("/search", response_model=List[MenuItem])
def search_menu_items(
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    dietary: Optional[str] = Query(None),
    flavor: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    query = select(MenuItem).where(MenuItem.is_available == True)

    if q:
        query = query.where(
            MenuItem.title.ilike(f"%{q}%") |
            MenuItem.description.ilike(f"%{q}%")
        )
    if origin:
        query = query.where(MenuItem.origin == origin)
    if category:
        query = query.where(MenuItem.category == category)
    if dietary:
        query = query.where(dietary == any_(MenuItem.dietary_features))
    if flavor:
        query = query.where(flavor == any_(MenuItem.flavor_profiles))
    if min_price is not None:
        query = query.where(MenuItem.price >= min_price)
    if max_price is not None:
        query = query.where(MenuItem.price <= max_price)

    return session.exec(query).all()


# -------------------------------
# Admin UI page
# -------------------------------
@router.get("/new")
def admin_new_menu_page(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse(request, "menu_new.html", {})


# -------------------------------
# Individual menu item detail page (HTML)
# -------------------------------
@router.get("/item/{item_id}")
def view_menu_item_page(
    item_id: UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    # Get menu item
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Get reviews with user info
    reviews_query = session.exec(
        select(Review, User)
        .join(User, Review.user_id == User.id)
        .where(Review.menu_item_id == item_id)
        .order_by(Review.created_at.desc())
    ).all()

    reviews = []
    total_rating = 0
    for review, user in reviews_query:
        reviews.append({
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email.split('@')[0],
            "avatar_url": user.avatar_url or "/static/images/default_user_profile.jpg",
        })
        total_rating += review.rating

    avg_rating = round(total_rating / len(reviews), 1) if reviews else 0

    cart_count = get_cart_count(request)
    logged_in_user = request.session.get("user")

    return templates.TemplateResponse(
        request,
        "menu_item_detail.html",
        {
            "item": item,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "review_count": len(reviews),
            "cart_count": cart_count,
            "user": logged_in_user,
        },
    )


# -------------------------------
# Get item by ID (API JSON)
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
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    origin: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    flavor_profiles: Optional[str] = Form(None),
    dietary_features: Optional[List[str]] = Form(None),
    recipe: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    session: Session = Depends(get_session),
    user=Depends(require_admin),
):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # String updates
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    if price is not None:
        item.price = price
    if category is not None:
        item.category = category
    if origin is not None:
        item.origin = origin

    if tags is not None:
        item.tags = _parse_csv_or_list(tags)
    if flavor_profiles is not None:
        item.flavor_profiles = _parse_csv_or_list(flavor_profiles)
    if dietary_features is not None:
        item.dietary_features = _parse_csv_or_list(dietary_features)
    if recipe is not None:
        item.recipe = recipe

    # Availability
    if is_available is not None:
        item.is_available = is_available

    # Image upload (append gallery; replace hero only if primary image provided)
    uploaded_files: List[UploadFile] = []
    if image:
        uploaded_files.append(image)
    if images:
        uploaded_files.extend(images)

    if uploaded_files:
        uploaded_urls: List[str] = []
        for f in uploaded_files:
            if not f.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files are allowed")
            uploaded_urls.append(upload_file_to_s3(f, folder="menu", bucket=S3_BUCKET_IMAGE))

        existing_gallery = item.gallery_urls or []

        # If admin uploaded a new primary image, replace hero with first uploaded
        if image:
            item.image_url = uploaded_urls[0]
            new_gallery = uploaded_urls[1:]
        else:
            # No primary image provided; treat all as gallery additions
            new_gallery = uploaded_urls

        # Append new gallery images to existing list
        item.gallery_urls = existing_gallery + new_gallery

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
    user=Depends(require_admin),
):
    item = session.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"detail": "Item deleted"}
