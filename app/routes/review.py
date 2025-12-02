from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from uuid import UUID
from typing import List
from app.core.db import get_session
from app.models.postgres.review import Review
from app.models.postgres.user import User
from app.models.postgres.menu import MenuItem

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/create")
def add_review(
    request: Request,
    menu_item_id: UUID = Form(...),
    rating: int = Form(...),
    comment: str = Form(...),
    session: Session = Depends(get_session),
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    # Check if menu item exists
    menu_item = session.get(MenuItem, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    user_id = UUID(user["id"])

    # Upsert: update existing review instead of allowing duplicates
    existing = session.exec(
        select(Review).where(
            Review.user_id == user_id,
            Review.menu_item_id == menu_item_id,
        )
    ).first()

    if existing:
        existing.rating = rating
        existing.comment = comment
        existing.created_at = datetime.utcnow()
    else:
        review = Review(
            user_id=user_id,
            menu_item_id=menu_item_id,
            rating=rating,
            comment=comment,
        )
        session.add(review)

    session.commit()

    # Redirect back to menu item page
    return RedirectResponse(url=f"/menu/item/{menu_item_id}", status_code=303)


@router.get("/menu/{menu_item_id}")
def get_reviews_for_item(
    menu_item_id: UUID,
    session: Session = Depends(get_session),
):
    """Get all reviews for a specific menu item with user info"""
    reviews = session.exec(
        select(Review, User)
        .join(User, Review.user_id == User.id)
        .where(Review.menu_item_id == menu_item_id)
        .order_by(Review.created_at.desc())
    ).all()

    result = []
    for review, user in reviews:
        result.append({
            "id": str(review.id),
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat(),
            "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email.split('@')[0],
            "avatar_url": user.avatar_url or "/static/images/default_user_profile.jpg"
        })

    return result
