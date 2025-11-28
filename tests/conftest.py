import os
import sys
import types
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Ensure a DATABASE_URL exists so main import doesn't fail; session is overridden in tests.
os.environ.setdefault("DATABASE_URL", "sqlite://")

# Ensure frontend dist exists so StaticFiles mount in main.py doesn't fail
frontend_dist = Path("ai_demo_frontend/dist")
frontend_dist.mkdir(parents=True, exist_ok=True)
index_file = frontend_dist / "index.html"
if not index_file.exists():
    index_file.write_text("<!doctype html><html><body>placeholder</body></html>")

# Stub out problematic type annotations (Python 3.9 lacks `str | None` support)
if "app.models.postgres.music" not in sys.modules:
    music_stub = types.ModuleType("app.models.postgres.music")
    class MusicTrack:
        __tablename__ = "music_track"
    music_stub.MusicTrack = MusicTrack
    sys.modules["app.models.postgres.music"] = music_stub

# Stub music routes to avoid Python 3.9 PEP604 unions in that module
if "app.routes.music" not in sys.modules:
    from fastapi import APIRouter
    music_routes_stub = types.ModuleType("app.routes.music")
    music_routes_stub.router = APIRouter(prefix="/music", tags=["Music"])
    sys.modules["app.routes.music"] = music_routes_stub

from main import app
from app.core import db, security
from app.models.postgres.menu import MenuItem
from app.models.postgres.review import Review
from app.models.postgres.user import User
from app.models.postgres.order import Order
from app.models.postgres.event import Event
from app.routes import menu as menu_routes
from app.routes import event as event_routes
from app.routes import cart as cart_routes


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
        self.users = []
        self.orders = []
        self.order_items = []
        self.events = []
        self.commits = 0

    def get(self, model, obj_id):
        if model is MenuItem:
            return self.menu_items.get(obj_id)
        if model is Review:
            for r in self.reviews:
                if r.id == obj_id:
                    return r
        if model is User:
            for u in self.users:
                if u.id == obj_id:
                    return u
        if model is Order:
            for o in self.orders:
                if o.id == obj_id:
                    return o
        if model is Event:
            for e in self.events:
                if e.id == obj_id:
                    return e
        return None

    def exec(self, statement):
        froms = statement.get_final_froms()
        table_name = froms[0].name if froms else ""

        if table_name == "menu_item":
            items = list(self.menu_items.values())
            # Basic is_available filter
            items = [i for i in items if getattr(i, "is_available", False)]
            params = statement.compile().params
            ids_filter = params.get("id_1") or params.get("id_2")
            if ids_filter:
                ids_as_str = {str(i) for i in ids_filter} if isinstance(ids_filter, (list, tuple, set)) else {str(ids_filter)}
                items = [i for i in items if str(i.id) in ids_as_str]
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

        if table_name == "user_account":
            params = statement.compile().params
            email = params.get("email_1")
            results = self.users
            if email is not None:
                results = [u for u in results if u.email == email]
            return FakeResult(results)

        if table_name == "order":
            params = statement.compile().params
            user_id = params.get("user_id_1")
            results = self.orders
            if user_id is not None:
                results = [o for o in results if str(getattr(o, "user_id", "")) == str(user_id)]
            return FakeResult(results)

        if table_name == "event":
            params = statement.compile().params
            results = self.events
            if "is_active_1" in params:
                results = [e for e in results if getattr(e, "is_active", None) == params["is_active_1"]]
            return FakeResult(results)

        return FakeResult([])

    def add(self, obj):
        if isinstance(obj, MenuItem):
            self.menu_items[obj.id] = obj
        elif isinstance(obj, Review):
            self.reviews.append(obj)
        elif isinstance(obj, User):
            self.users.append(obj)
        elif isinstance(obj, Order):
            self.orders.append(obj)
        elif hasattr(obj, "__class__") and obj.__class__.__name__ == "OrderItem":
            self.order_items.append(obj)
        elif isinstance(obj, Event):
            self.events.append(obj)

    def delete(self, obj):
        if isinstance(obj, MenuItem):
            self.menu_items.pop(obj.id, None)
        elif isinstance(obj, Review):
            if obj in self.reviews:
                self.reviews.remove(obj)
        elif isinstance(obj, User):
            if obj in self.users:
                self.users.remove(obj)
        elif isinstance(obj, Order):
            if obj in self.orders:
                self.orders.remove(obj)
        elif isinstance(obj, Event):
            if obj in self.events:
                self.events.remove(obj)

    def commit(self):
        self.commits += 1

    def rollback(self):
        # Provide rollback to mirror real session API used in routes
        return None

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
    # Force event routes to use fake session instead of real DB engine
    class _SessionCtx:
        def __init__(self, fs):
            self.fs = fs
        def __enter__(self):
            return self.fs
        def __exit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr(event_routes, "Session", lambda *_, **__: _SessionCtx(fake_session))
    monkeypatch.setattr(cart_routes, "Session", lambda *_, **__: _SessionCtx(fake_session))
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(fake_session, overrides):
    return TestClient(app, follow_redirects=False)
