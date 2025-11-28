from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.routes.review import add_review
from app.models.postgres.review import Review


def _make_request_with_user(user_id):
    scope = {"type": "http", "headers": [], "session": {"user": {"id": str(user_id)}}}
    return Request(scope)


def test_add_review_inserts_then_updates_existing_review(fake_session):
    user_id = uuid4()
    menu_item_id = uuid4()
    fake_session.menu_items[menu_item_id] = object()  # truthy placeholder for menu item
    request = _make_request_with_user(user_id)

    # First create
    resp = add_review(
        request=request,
        menu_item_id=menu_item_id,
        rating=4,
        comment="Tasty",
        session=fake_session,
    )
    assert resp.status_code == 303
    assert len(fake_session.reviews) == 1
    created = fake_session.reviews[0]
    assert created.rating == 4
    assert created.comment == "Tasty"

    # Update same user/item
    resp = add_review(
        request=request,
        menu_item_id=menu_item_id,
        rating=2,
        comment="Changed mind",
        session=fake_session,
    )
    assert resp.status_code == 303
    assert len(fake_session.reviews) == 1
    updated = fake_session.reviews[0]
    assert updated.rating == 2
    assert updated.comment == "Changed mind"
    assert fake_session.commits == 2


def test_add_review_requires_login(fake_session):
    request = Request({"type": "http", "headers": [], "session": {}})
    with pytest.raises(HTTPException) as exc:
        add_review(
            request=request,
            menu_item_id=uuid4(),
            rating=5,
            comment="Nice",
            session=fake_session,
        )
    assert exc.value.status_code == 401


