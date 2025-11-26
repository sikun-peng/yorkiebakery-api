import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Ensure a DATABASE_URL exists so main import doesn't fail; session is overridden in tests.
os.environ.setdefault("DATABASE_URL", "sqlite://")

from main import app
from app.core import db, security
from app.models.postgres.menu import MenuItem
from app.models.postgres.review import Review
from app.routes import menu as menu_routes


class FakeResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def all(self):
        return list(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None


class FakeSession:
    def __init__(self):
        self.menu_items = {}
        self.reviews = []
        self.commits = 0

    def get(self, model, obj_id):
        if model is MenuItem:
            return self.menu_items.get(obj_id)
        if model is Review:
            for r in self.reviews:
                if r.id == obj_id:
                    return r
        return None

    def exec(self, statement):
        froms = statement.get_final_froms()
        table_name = froms[0].name if froms else ""

        if table_name == "menu_item":
            items = list(self.menu_items.values())
            # Basic is_available filter
            items = [i for i in items if getattr(i, "is_available", False)]
            return FakeResult(items)

        if table_name == "review":
            params = statement.compile().params
            user_id = params.get("user_id_1")
            menu_item_id = params.get("menu_item_id_1")
            results = self.reviews
            if user_id is not None:
                results = [r for r in results if r.user_id == user_id]
            if menu_item_id is not None:
                results = [r for r in results if r.menu_item_id == menu_item_id]
            return FakeResult(results)

        return FakeResult([])

    def add(self, obj):
        if isinstance(obj, MenuItem):
            self.menu_items[obj.id] = obj
        elif isinstance(obj, Review):
            self.reviews.append(obj)

    def delete(self, obj):
        if isinstance(obj, MenuItem):
            self.menu_items.pop(obj.id, None)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        # No-op for fake session
        return obj


@pytest.fixture
def fake_session():
    session = FakeSession()
    # Seed one available item
    seed = MenuItem(
        id=uuid4(),
        title="Seeded Item",
        description="Test item",
        price=9.99,
        category="dessert",
        origin="french",
        tags=["sweet"],
        flavor_profiles=["sweet"],
        dietary_features=["vegetarian"],
        is_available=True,
        image_url="https://example.com/seed.jpg",
    )
    session.menu_items[seed.id] = seed
    return session


@pytest.fixture(autouse=True)
def overrides(fake_session, monkeypatch):
    def _get_session():
        yield fake_session

    app.dependency_overrides[db.get_session] = _get_session
    app.dependency_overrides[security.require_admin] = lambda: {"role": "admin"}
    monkeypatch.setattr(menu_routes, "upload_file_to_s3", lambda *_, **__: "https://example.com/uploaded.jpg")
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(fake_session, overrides):
    return TestClient(app)
