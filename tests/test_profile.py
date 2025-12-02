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


def test_profile_address_save_and_clear(client, profile_user):
    # Log in
    login_resp = client.post(
        "/auth/login_form",
        data={"email": profile_user.email, "password": "secret123"},
    )
    assert login_resp.status_code in (200, 303)

    # Save default address
    resp = client.post(
        "/profile/address",
        data={
            "address_line1": "123 Bakery Ln",
            "address_line2": "Apt 5",
            "city": "Portland",
            "state": "OR",
            "postal_code": "97205",
            "country": "USA",
            "default_phone": "555-0000",
        },
    )
    assert resp.status_code == 303
    assert profile_user.address_line1 == "123 Bakery Ln"
    assert profile_user.address_line2 == "Apt 5"
    assert profile_user.city == "Portland"
    assert profile_user.state == "OR"
    assert profile_user.postal_code == "97205"
    assert profile_user.country == "USA"
    assert profile_user.default_phone == "555-0000"

    # Clear saved address
    resp_clear = client.post(
        "/profile/address",
        data={
            "address_line1": "",
            "address_line2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "country": "",
            "default_phone": "",
        },
    )
    assert resp_clear.status_code == 303
    assert profile_user.address_line1 is None
    assert profile_user.address_line2 is None
    assert profile_user.city is None
    assert profile_user.state is None
    assert profile_user.postal_code is None
    assert profile_user.country is None
    assert profile_user.default_phone is None
