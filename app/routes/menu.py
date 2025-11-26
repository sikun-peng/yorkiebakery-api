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
from app.models.postgres.review import Review
from app.models.postgres.user import User
from app.core.db import get_session
from app.core.security import require_admin
from app.core.cart_utils import get_cart_count
from app.utils.s3_util import upload_file_to_s3

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/menu", tags=["Menu"])

S3_BUCKET_IMAGE = "yorkiebakery-image"


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
        # Get all items first
        all_items = session.exec(select(MenuItem).where(MenuItem.is_available == True)).all()

        # Apply dietary filters in Python if provided
        if dietary:
            filtered_items = []
            for item in all_items:
                # Check if item has ALL of the requested dietary features (AND logic)
                if item.dietary_features and all(diet in item.dietary_features for diet in dietary):
                    filtered_items.append(item)
            items = filtered_items
        else:
            items = all_items

        # Get review counts and average ratings for all items
        review_stats = {}
        for item in items:
            reviews = session.exec(
                select(Review)
                .where(Review.menu_item_id == item.id)
            ).all()

            if reviews:
                total_rating = sum(r.rating for r in reviews)
                avg_rating = round(total_rating / len(reviews), 1)
                review_stats[str(item.id)] = {
                    "count": len(reviews),
                    "avg_rating": avg_rating
                }
            else:
                review_stats[str(item.id)] = {
                    "count": 0,
                    "avg_rating": 0
                }

        cart = request.session.get("cart", {})
        cart_count = sum(cart.values())

        return templates.TemplateResponse(
            "menu.html",
            {
                "request": request,
                "items": items,
                "cart": cart,
                "cart_count": cart_count,
                "review_stats": review_stats,
            },
        )
    except Exception as e:
        print(f"Error in view_menu_page: {e}")
        # Return empty response on error
        return templates.TemplateResponse(
            "menu.html",
            {
                "request": request,
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
    dietary_features: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    user=Depends(require_admin),
):
    # Validate image type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Upload image to S3
    image_url = upload_file_to_s3(image, folder="menu", bucket=S3_BUCKET_IMAGE)

    # Convert CSV → list[]
    def parse_list(value: Optional[str]):
        if not value:
            return []
        return [v.strip() for v in value.split(",") if v.strip()]

    item = MenuItem(
        title=title,
        description=description,
        price=float(price),
        category=category,
        origin=origin,
        tags=parse_list(tags),
        flavor_profiles=parse_list(flavor_profiles),
        dietary_features=parse_list(dietary_features),
        image_url=image_url,
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
    return templates.TemplateResponse("menu_new.html", {"request": request})


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
            "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email.split('@')[0]
        })
        total_rating += review.rating

    avg_rating = round(total_rating / len(reviews), 1) if reviews else 0

    cart_count = get_cart_count(request)
    logged_in_user = request.session.get("user")

    return templates.TemplateResponse(
        "menu_item_detail.html",
        {
            "request": request,
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
    dietary_features: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
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

    # List fields (CSV → list)
    def parse_list(value):
        if value is None:
            return None
        return [v.strip() for v in value.split(",") if v.strip()]

    if tags is not None:
        item.tags = parse_list(tags)
    if flavor_profiles is not None:
        item.flavor_profiles = parse_list(flavor_profiles)
    if dietary_features is not None:
        item.dietary_features = parse_list(dietary_features)

    # Availability
    if is_available is not None:
        item.is_available = is_available

    # Image upload
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