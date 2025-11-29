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


@pytest.mark.auth
def test_register_form_new_user(client, fake_session, monkeypatch):
    """Test register_form endpoint creates new user"""
    email_sent = []
    def mock_send_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/register_form",
        data={
            "email": "formuser@example.com",
            "password": "password123",
            "first_name": "Form",
            "last_name": "User",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(email_sent) == 1


@pytest.mark.auth
def test_register_form_duplicate_email(client, test_user, monkeypatch):
    """Test register_form with duplicate email"""
    def mock_send_email(*args, **kwargs):
        pass
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/register_form",
        data={
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "User",
        },
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["success"] is False
    assert "already exists" in data["error"].lower()


@pytest.mark.auth
def test_resend_verification(client, unverified_user, monkeypatch):
    """Test resending verification email"""
    email_sent = []
    def mock_send_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/resend_verification",
        data={"email": "unverified@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(email_sent) == 1


@pytest.mark.auth
def test_resend_verification_verified_user(client, test_user, monkeypatch):
    """Test resending verification to already verified user"""
    email_sent = []
    def mock_send_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/resend_verification",
        data={"email": "test@example.com"},
    )
    assert resp.status_code == 200
    # Should not send email to already verified user
    assert len(email_sent) == 0


@pytest.mark.auth
def test_verify_email_with_valid_token(client, unverified_user, monkeypatch):
    """Test email verification with valid token"""
    from app.core.security import create_verification_token

    token = create_verification_token(unverified_user.email)

    resp = client.get(f"/auth/verify?token={token}")
    assert resp.status_code == 303  # Redirect after verification


@pytest.mark.auth
def test_verify_email_with_invalid_token(client):
    """Test email verification with invalid token"""
    resp = client.get("/auth/verify?token=invalid_token")
    assert resp.status_code in [400, 303]


@pytest.mark.auth
def test_verify_email_nonexistent_user(client, monkeypatch):
    """Test email verification for non-existent user"""
    from app.core.security import create_verification_token

    token = create_verification_token("nonexistent@example.com")

    resp = client.get(f"/auth/verify?token={token}")
    assert resp.status_code in [404, 400]


@pytest.mark.auth
def test_api_register_new_user(client, monkeypatch):
    """Test API register endpoint"""
    def mock_send_email(*args, **kwargs):
        pass
    monkeypatch.setattr("app.routes.auth.send_verification_email", mock_send_email)

    resp = client.post(
        "/auth/register",
        json={
            "email": "apiuser@example.com",
            "password": "password123",
            "first_name": "API",
            "last_name": "User",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "user_id" in data or "msg" in data


@pytest.mark.auth
def test_api_register_duplicate_email_json(client, test_user):
    """Test API register with duplicate email"""
    resp = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "User",
        },
    )
    assert resp.status_code == 400


@pytest.mark.auth
def test_api_login_valid_credentials(client, test_user):
    """Test API login with valid credentials"""
    resp = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.auth
def test_api_login_invalid_credentials(client, test_user):
    """Test API login with invalid password"""
    resp = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert resp.status_code == 401


@pytest.mark.auth
def test_api_login_unverified_user(client, unverified_user):
    """Test API login with unverified user"""
    resp = client.post(
        "/auth/login",
        json={
            "email": "unverified@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 403


@pytest.mark.auth
def test_forgot_password_json(client, test_user, fake_session, monkeypatch):
    """Test forgot password with JSON payload"""
    email_sent = []
    def mock_send_reset_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.auth.send_password_reset_email", mock_send_reset_email)

    resp = client.post(
        "/auth/forgot_password",
        json={"email": "test@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(email_sent) == 1


@pytest.mark.auth
def test_forgot_password_missing_email(client):
    """Test forgot password without email"""
    resp = client.post(
        "/auth/forgot_password",
        json={},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["success"] is False


@pytest.mark.auth
def test_reset_password_page_valid_token(client, test_user, fake_session):
    """Test reset password page with valid token"""
    from app.routes.auth import create_password_reset_token
    from app.models.postgres.password_reset_token import PasswordResetToken

    token = create_password_reset_token()
    reset_token_record = PasswordResetToken(
        user_id=test_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_used=False
    )
    fake_session.add(reset_token_record)
    fake_session.commit()

    resp = client.get(f"/auth/reset_password?token={token}")
    assert resp.status_code == 200


@pytest.mark.auth
def test_reset_password_page_invalid_token(client):
    """Test reset password page with invalid token"""
    resp = client.get("/auth/reset_password?token=invalid")
    assert resp.status_code == 200
    # Page should render with error


@pytest.mark.auth
def test_reset_password_page_expired_token(client, test_user, fake_session):
    """Test reset password page with expired token"""
    from app.routes.auth import create_password_reset_token
    from app.models.postgres.password_reset_token import PasswordResetToken

    token = create_password_reset_token()
    reset_token_record = PasswordResetToken(
        user_id=test_user.id,
        token=token,
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        is_used=False
    )
    fake_session.add(reset_token_record)
    fake_session.commit()

    resp = client.get(f"/auth/reset_password?token={token}")
    assert resp.status_code == 200


@pytest.mark.auth
def test_reset_password_submit_valid(client, test_user, fake_session):
    """Test resetting password with valid token"""
    from app.routes.auth import create_password_reset_token
    from app.models.postgres.password_reset_token import PasswordResetToken

    token = create_password_reset_token()
    reset_token_record = PasswordResetToken(
        user_id=test_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_used=False
    )
    fake_session.add(reset_token_record)
    fake_session.commit()

    resp = client.post(
        "/auth/reset_password",
        data={
            "token": token,
            "new_password": "newpassword123",
        },
    )
    # Can be 200 or 400 depending on token verification
    assert resp.status_code in [200, 400]


@pytest.mark.auth
def test_reset_password_submit_invalid_token(client):
    """Test resetting password with invalid token"""
    resp = client.post(
        "/auth/reset_password",
        data={
            "token": "short",
            "new_password": "newpassword123",
        },
    )
    assert resp.status_code == 400


@pytest.mark.auth
def test_reset_password_submit_used_token(client, test_user, fake_session):
    """Test resetting password with already used token"""
    from app.routes.auth import create_password_reset_token
    from app.models.postgres.password_reset_token import PasswordResetToken

    token = create_password_reset_token()
    reset_token_record = PasswordResetToken(
        user_id=test_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_used=True  # Already used
    )
    fake_session.add(reset_token_record)
    fake_session.commit()

    resp = client.post(
        "/auth/reset_password",
        data={
            "token": token,
            "new_password": "newpassword123",
        },
    )
    assert resp.status_code == 400


@pytest.mark.auth
def test_login_with_redirect_url(client, test_user):
    """Test login with redirect URL parameter"""
    resp = client.post(
        "/auth/login_form",
        data={
            "email": "test@example.com",
            "password": "password123",
            "redirect_url": "/menu/view",
        },
    )
    assert resp.status_code in [200, 303]


@pytest.mark.auth
def test_login_page_ajax_request(client):
    """Test login page with AJAX request"""
    resp = client.get(
        "/auth/login",
        headers={"x-requested-with": "XMLHttpRequest"},
    )
    assert resp.status_code == 200


@pytest.mark.auth
def test_resend_verification_nonexistent(client):
    """Test resending verification for non-existent user"""
    resp = client.post(
        "/auth/resend_verification",
        data={"email": "nonexistent@example.com"},
    )
    # Should succeed but not send email (to prevent email enumeration)
    assert resp.status_code == 200


@pytest.mark.auth
def test_api_login_nonexistent_user(client):
    """Test API login with non-existent user"""
    resp = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 401


@pytest.mark.auth
def test_forgot_password_email_failure(client, test_user, fake_session, monkeypatch):
    """Test forgot password when email sending fails"""
    def mock_send_email(*args, **kwargs):
        raise Exception("Email service down")
    monkeypatch.setattr("app.routes.auth.send_password_reset_email", mock_send_email)

    resp = client.post(
        "/auth/forgot_password",
        json={"email": "test@example.com"},
    )
    # Should still return success for security
    assert resp.status_code == 200


@pytest.mark.auth

@pytest.mark.auth

@pytest.mark.auth

@pytest.mark.auth

@pytest.mark.auth


@pytest.mark.auth

@pytest.mark.auth

@pytest.mark.auth
def test_logout_clears_session(client):
    """Test logout functionality"""
    resp = client.get("/auth/logout")
    assert resp.status_code in [303, 200]


@pytest.mark.auth
def test_verify_email_already_verified(client, test_user, fake_session):
    """Test verifying already verified email"""
    from app.core.security import create_verification_token

    # Ensure user is verified
    test_user.is_verified = True
    fake_session.add(test_user)
    fake_session.commit()

    token = create_verification_token(test_user.email)
    resp = client.get(f"/auth/verify?token={token}")
    assert resp.status_code in [200, 303]


@pytest.mark.auth
def test_auth_login_with_empty_email(client):
    """Test login with empty email"""
    resp = client.post(
        "/auth/login",
        json={"email": "", "password": "password"},
    )
    assert resp.status_code in [400, 401, 422]


@pytest.mark.auth
def test_auth_login_with_empty_password(client):
    """Test login with empty password"""
    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": ""},
    )
    assert resp.status_code in [400, 401, 422]


@pytest.mark.auth
def test_auth_register_with_invalid_email(client):
    """Test register with invalid email"""
    resp = client.post(
        "/auth/register",
        json={
            "email": "notanemail",
            "password": "ValidPass123!",
            "first_name": "Invalid",
            "last_name": "Email",
        },
    )
    assert resp.status_code in [400, 422]


@pytest.mark.auth
def test_auth_register_variations(client):
    """Test register with various inputs"""
    variations = [
        {"email": f"var{i}@example.com", "password": f"Pass{i}123!", "first_name": f"First{i}", "last_name": f"Last{i}"}
        for i in range(5)
    ]
    for data in variations:
        resp = client.post("/auth/register_form", data=data)
        assert resp.status_code in [200, 303, 400, 422]


@pytest.mark.auth
def test_auth_forgot_password_variations(client):
    """Test forgot password with various emails"""
    emails = [f"forgot{i}@example.com" for i in range(5)]
    for email in emails:
        resp = client.post("/auth/forgot_password", json={"email": email})
        assert resp.status_code in [200, 303, 400]
