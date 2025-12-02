import pytest
from uuid import uuid4
from datetime import datetime

from app.models.postgres.user import User
from app.core.security import hash_password


@pytest.fixture
def profile_user(fake_session):
    user = User(
        id=uuid4(),
        email="profile@test.com",
        password_hash=hash_password("secret123"),
        first_name="Profile",
        last_name="User",
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


def test_profile_requires_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 303
    assert "/auth/login" in resp.headers.get("location", "")


def test_profile_renders_for_logged_in_user(client, profile_user):
    # Log in to establish session cookie
    login_resp = client.post(
        "/auth/login_form",
        data={"email": profile_user.email, "password": "secret123"},
    )
    assert login_resp.status_code in (200, 303)

    resp = client.get("/profile")
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "My Profile" in body
    assert profile_user.email in body
