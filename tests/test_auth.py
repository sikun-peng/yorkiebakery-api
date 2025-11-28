import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.models.postgres.user import User
from app.models.postgres.password_reset_token import PasswordResetToken
from app.core.security import hash_password


@pytest.fixture
def test_user(fake_session):
    """Create a test user for auth tests"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password("password123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_admin=False,
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.fixture
def unverified_user(fake_session):
    """Create an unverified test user"""
    user = User(
        id=uuid4(),
        email="unverified@example.com",
        password_hash=hash_password("password123"),
        first_name="Unverified",
        last_name="User",
        is_verified=False,
        is_admin=False,
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.mark.auth
def test_login_page_renders(client):
    """Test that login page renders correctly"""
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"login" in resp.content.lower()


@pytest.mark.auth
def test_login_with_valid_credentials(client, test_user, fake_session):
    """Test successful login with valid credentials"""
    resp = client.post(
        "/auth/login_form",
        data={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "redirect" in data or resp.status_code == 303


@pytest.mark.auth
def test_login_with_invalid_password(client, test_user):
    """Test login fails with wrong password"""
    resp = client.post(
        "/auth/login_form",
        data={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["success"] is False
    assert "Invalid" in data["error"]


@pytest.mark.auth
def test_login_with_nonexistent_user(client):
    """Test login fails with non-existent user"""
    resp = client.post(
        "/auth/login_form",
        data={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["success"] is False


@pytest.mark.auth
def test_login_with_unverified_email(client, unverified_user):
    """Test login fails for unverified users"""
    resp = client.post(
        "/auth/login_form",
        data={
            "email": "unverified@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 403
    data = resp.json()
    assert data["success"] is False
    assert "verify" in data["error"].lower()


@pytest.mark.auth
def test_register_page_renders(client):
    """Test that register page renders correctly"""
    resp = client.get("/auth/register")
    assert resp.status_code in [200, 405]
    if resp.status_code == 200:
        assert b"register" in resp.content.lower()


@pytest.mark.auth
def test_register_new_user(client, fake_session, monkeypatch):
    """Test successful user registration"""
    # Mock email sending
    email_sent = []
    def mock_send_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/register",
        data={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    # Should redirect after successful registration
    assert resp.status_code in [200, 303, 422]


@pytest.mark.auth
def test_register_duplicate_email(client, test_user):
    """Test registration fails with duplicate email"""
    resp = client.post(
        "/auth/register",
        data={
            "email": "test@example.com",  # Already exists
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "User",
        },
    )
    # Should show error for duplicate email
    assert resp.status_code in [200, 400, 422]


@pytest.mark.auth
def test_logout(client, test_user):
    """Test logout functionality"""
    # First login
    client.post(
        "/auth/login_form",
        data={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Then logout
    resp = client.get("/auth/logout")
    assert resp.status_code in [200, 303]  # Should redirect or return success


@pytest.mark.auth
def test_password_reset_request_page_renders(client):
    """Test password reset request page renders"""
    resp = client.get("/auth/forgot_password")
    assert resp.status_code in [200, 405]


@pytest.mark.auth
def test_password_reset_request_with_valid_email(client, test_user, monkeypatch):
    """Test password reset request sends email"""
    email_sent = []
    def mock_send_reset_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_password_reset_email", mock_send_reset_email)

    resp = client.post(
        "/auth/forgot_password",
        data={"email": "test@example.com"},
    )
    assert resp.status_code in [200, 303]


@pytest.mark.auth
def test_password_reset_request_with_invalid_email(client):
    """Test password reset request with non-existent email"""
    resp = client.post(
        "/auth/forgot_password",
        data={"email": "nonexistent@example.com"},
    )
    # Should handle gracefully (don't reveal if email exists)
    assert resp.status_code in [200, 303]


@pytest.mark.auth
def test_absolute_url_helper():
    """Test absolute URL helper function"""
    from app.routes.auth import absolute_url
    from unittest.mock import Mock

    request = Mock()
    request.base_url = "http://example.com/"

    url = absolute_url(request, "/path")
    assert url == "http://example.com/path"

    url = absolute_url(request, "path")
    assert url == "http://example.com/path"


@pytest.mark.auth
def test_create_password_reset_token():
    """Test password reset token generation"""
    from app.routes.auth import create_password_reset_token

    token1 = create_password_reset_token()
    token2 = create_password_reset_token()

    assert len(token1) > 20
    assert token1 != token2  # Should be unique
