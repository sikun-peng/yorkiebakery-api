import strawberry
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select
from sqlalchemy import literal
from strawberry.fastapi import GraphQLRouter
from strawberry.exceptions import GraphQLError
from fastapi import Request

from app.core.db import engine
from app.models.postgres.menu import MenuItem
from app.models.postgres.review import Review
from app.models.postgres.user import User


def _user_name(user: Optional[User]) -> str:
    if not user:
        return "Guest"
    name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
    return name or (user.email.split("@")[0] if user.email else "User")


@strawberry.type
class UserLite:
    id: strawberry.ID
    email: str
    name: str


@strawberry.type
class ReviewType:
    id: strawberry.ID
    rating: int
    comment: str
    created_at: datetime
    user: UserLite


@strawberry.type
class MenuItemType:
    id: strawberry.ID
    title: str
    description: Optional[str]
    category: Optional[str]
    price: float
    tags: List[str]
    flavor_profiles: List[str]
    dietary_features: List[str]
    image_url: Optional[str]

    @strawberry.field
    def reviews(self, info, limit: int = 10, offset: int = 0) -> List[ReviewType]:
        with Session(engine) as session:
            rows = session.exec(
                select(Review, User)
                .join(User, User.id == Review.user_id, isouter=True)
                .where(Review.menu_item_id == UUID(str(self.id)))
                .order_by(Review.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
            results: List[ReviewType] = []
            for review, user in rows:
                results.append(
                    ReviewType(
                        id=str(review.id),
                        rating=review.rating,
                        comment=review.comment,
                        created_at=review.created_at,
                        user=UserLite(id=str(user.id), email=user.email, name=_user_name(user)) if user else UserLite(id="unknown", email="", name="Guest"),
                    )
                )
            return results


def _to_menu_item(mi: MenuItem) -> MenuItemType:
    return MenuItemType(
        id=str(mi.id),
        title=mi.title,
        description=mi.description,
        category=mi.category,
        price=float(mi.price or 0),
        tags=mi.tags or [],
        flavor_profiles=mi.flavor_profiles or [],
        dietary_features=mi.dietary_features or [],
        image_url=mi.image_url,
    )


@strawberry.type
class Query:
    @strawberry.field
    def menu_item(self, id: strawberry.ID) -> Optional[MenuItemType]:
        with Session(engine) as session:
            mi = session.get(MenuItem, UUID(str(id)))
            if not mi:
                return None
            return _to_menu_item(mi)

    @strawberry.field
    def menu_items(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[MenuItemType]:
        with Session(engine) as session:
            query = select(MenuItem).where(MenuItem.is_available == True)  # noqa: E712
            if category:
                query = query.where(MenuItem.category == category)
            if tags:
                # Require each tag to be present; use ANY for compatibility
                for tag in tags:
                    query = query.where(MenuItem.tags.any(tag))
            items = session.exec(query.offset(offset).limit(limit)).all()
            return [_to_menu_item(mi) for mi in items]

    @strawberry.field
    def reviews(
        self,
        menu_item_id: strawberry.ID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ReviewType]:
        with Session(engine) as session:
            rows = session.exec(
                select(Review, User)
                .join(User, User.id == Review.user_id, isouter=True)
                .where(Review.menu_item_id == UUID(str(menu_item_id)))
                .order_by(Review.created_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
            results: List[ReviewType] = []
            for review, user in rows:
                results.append(
                    ReviewType(
                        id=str(review.id),
                        rating=review.rating,
                        comment=review.comment,
                        created_at=review.created_at,
                        user=UserLite(id=str(user.id), email=user.email, name=_user_name(user)) if user else UserLite(id="unknown", email="", name="Guest"),
                    )
                )
            return results


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_review(self, info, menu_item_id: strawberry.ID, rating: int, comment: str) -> ReviewType:
        request: Request = info.context["request"]
        user_session = request.session.get("user")
        if not user_session:
            raise GraphQLError("Login required to add a review.")

        if rating < 1 or rating > 5:
            raise GraphQLError("Rating must be between 1 and 5.")

        with Session(engine) as session:
            mi = session.get(MenuItem, UUID(str(menu_item_id)))
            if not mi:
                raise GraphQLError("Menu item not found.")

            user = session.get(User, UUID(str(user_session["id"])))
            if not user:
                raise GraphQLError("User not found.")

            # Upsert: update existing review if present
            existing = session.exec(
                select(Review).where(
                    Review.user_id == user.id,
                    Review.menu_item_id == mi.id
                )
            ).first()

            if existing:
                existing.rating = rating
                existing.comment = comment
                existing.created_at = datetime.utcnow()
                review_obj = existing
            else:
                review_obj = Review(
                    user_id=user.id,
                    menu_item_id=mi.id,
                    rating=rating,
                    comment=comment,
                    created_at=datetime.utcnow(),
                )
                session.add(review_obj)

            session.commit()
            session.refresh(review_obj)

            return ReviewType(
                id=str(review_obj.id),
                rating=review_obj.rating,
                comment=review_obj.comment,
                created_at=review_obj.created_at,
                user=UserLite(id=str(user.id), email=user.email, name=_user_name(user)),
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context(request: Request):
    return {"request": request}


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,
)
