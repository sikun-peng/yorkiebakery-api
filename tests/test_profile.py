import pytest
from uuid import uuid4
from datetime import datetime
from io import BytesIO
from app.models.postgres.user import User
from app.core.security import hash_password
from unittest.mock import Mock, MagicMock, patch, AsyncMock


@pytest.fixture
def test_user(fake_session):
    """Create a test user for profile tests"""
    user = User(
        id=uuid4(),
        email="profile@example.com",
        password_hash=hash_password("password123"),
        first_name="Profile",
        last_name="User",
        is_verified=True,
        is_admin=False,
        created_at=datetime.utcnow(),
        avatar_url="https://example.com/avatar/default.jpg",
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.mark.profile
def test_profile_page_unauthenticated(client):
    """Test profile page redirects to login when not authenticated"""
    resp = client.get("/profile")
    assert resp.status_code == 303
    assert "/auth/login" in resp.headers.get("location", "")


@pytest.mark.profile
def test_redirect_password_get(client):
    """Test GET /profile/password redirects to profile"""
    resp = client.get("/profile/password")
    assert resp.status_code == 303
    assert "/profile" in resp.headers.get("location", "")


@pytest.mark.profile
def test_redirect_name_get(client):
    """Test GET /profile/name redirects to profile"""
    resp = client.get("/profile/name")
    assert resp.status_code == 303
    assert "/profile" in resp.headers.get("location", "")


@pytest.mark.profile
def test_redirect_avatar_get(client):
    """Test GET /profile/avatar redirects to profile"""
    resp = client.get("/profile/avatar")
    assert resp.status_code == 303
    assert "/profile" in resp.headers.get("location", "")


@pytest.mark.profile
def test_update_name_unauthenticated(client):
    """Test name update fails when not authenticated"""
    resp = client.post(
        "/profile/name",
        data={
            "first_name": "NewFirst",
            "last_name": "NewLast",
        },
    )
    assert resp.status_code == 401


@pytest.mark.profile
def test_update_password_unauthenticated(client):
    """Test password update fails when not authenticated"""
    resp = client.post(
        "/profile/password",
        data={
            "current_password": "password123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
    )
    assert resp.status_code == 401


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_unauthenticated(client):
    """Test avatar upload fails when not authenticated"""
    file = ("file", ("avatar.jpg", BytesIO(b"fake image"), "image/jpeg"))

    resp = client.post(
        "/profile/avatar",
        files=[file],
    )
    assert resp.status_code == 401


@pytest.mark.profile
def test_require_user_no_session(client):
    """Test require_user raises 401 when no session"""
    from app.routes.profile import require_user
    from app.core.db import get_session
    from fastapi import Request, HTTPException

    # Create mock request with no session
    request = Mock(spec=Request)
    request.session = {}

    # Get session
    session = next(get_session())

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        require_user(request, session)
    assert exc_info.value.status_code == 401


@pytest.mark.profile
def test_require_user_user_not_found(client, fake_session):
    """Test require_user raises 404 when user not found"""
    from app.routes.profile import require_user
    from fastapi import Request, HTTPException

    # Create mock request with session containing non-existent user ID
    request = Mock(spec=Request)
    request.session = {"user": {"id": uuid4()}}

    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        require_user(request, fake_session)
    assert exc_info.value.status_code == 404


@pytest.mark.profile
def test_require_user_success(test_user, fake_session):
    """Test require_user returns user when authenticated"""
    from app.routes.profile import require_user
    from fastapi import Request

    # Create mock request with valid session
    request = Mock(spec=Request)
    request.session = {"user": {"id": test_user.id}}

    user = require_user(request, fake_session)
    assert user.id == test_user.id
    assert user.email == test_user.email


# Unit tests for route logic using direct function calls
@pytest.mark.profile
def test_update_name_logic(test_user, fake_session):
    """Test name update database logic"""
    from app.routes.profile import update_name
    from fastapi import Form
    from unittest.mock import MagicMock

    # Create mock request with session
    request = MagicMock()
    request.session = {"user": {"first_name": ""}}
    request.headers = {}

    # Mock require_user to return our test_user
    with patch("app.routes.profile.require_user", return_value=test_user):
        result = update_name(
            request=request,
            first_name="NewFirst",
            last_name="NewLast",
            session=fake_session,
        )

    # Verify redirect response
    assert result.status_code == 303

    # Verify database update
    updated_user = fake_session.get(User, test_user.id)
    assert updated_user.first_name == "NewFirst"
    assert updated_user.last_name == "NewLast"


@pytest.mark.profile
def test_update_name_empty_values(test_user, fake_session):
    """Test name update with empty values sets to None"""
    from app.routes.profile import update_name
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {"first_name": ""}}
    request.headers = {}

    with patch("app.routes.profile.require_user", return_value=test_user):
        update_name(
            request=request,
            first_name="",
            last_name="",
            session=fake_session,
        )

    # Verify database update
    updated_user = fake_session.get(User, test_user.id)
    assert updated_user.first_name is None
    assert updated_user.last_name is None


@pytest.mark.profile
def test_update_password_success(test_user, fake_session):
    """Test successful password update"""
    from app.routes.profile import update_password
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = update_password(
            request=request,
            current_password="password123",
            new_password="newpassword123",
            confirm_password="newpassword123",
            session=fake_session,
        )

    # Verify redirect response
    assert result.status_code == 303

    # Verify password was updated
    from app.core.security import verify_password
    updated_user = fake_session.get(User, test_user.id)
    assert verify_password("newpassword123", updated_user.password_hash)


@pytest.mark.profile
def test_update_password_mismatch(test_user, fake_session):
    """Test password update fails when passwords don't match"""
    from app.routes.profile import update_password
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = update_password(
            request=request,
            current_password="password123",
            new_password="newpassword123",
            confirm_password="differentpassword",
            session=fake_session,
        )

    # Verify error response
    assert result.status_code == 400


@pytest.mark.profile
def test_update_password_too_short(test_user, fake_session):
    """Test password update fails when new password is too short"""
    from app.routes.profile import update_password
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = update_password(
            request=request,
            current_password="password123",
            new_password="short",
            confirm_password="short",
            session=fake_session,
        )

    # Verify error response
    assert result.status_code == 400


@pytest.mark.profile
def test_update_password_wrong_current(test_user, fake_session):
    """Test password update fails with incorrect current password"""
    from app.routes.profile import update_password
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = update_password(
            request=request,
            current_password="wrongpassword",
            new_password="newpassword123",
            confirm_password="newpassword123",
            session=fake_session,
        )

    # Verify error response
    assert result.status_code == 400


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_invalid_mime_type(test_user, fake_session):
    """Test avatar upload fails with invalid file type"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile, HTTPException
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    # Create fake GIF file with mocked content_type
    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.gif"
    file.file = BytesIO(b"fake gif")
    file.content_type = "image/gif"
    file.read = BytesIO(b"fake gif").read

    with patch("app.routes.profile.require_user", return_value=test_user):
        with pytest.raises(HTTPException) as exc_info:
            await upload_avatar(request=request, file=file, session=fake_session)
        assert exc_info.value.status_code == 400


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_file_too_large(test_user, fake_session):
    """Test avatar upload fails when file is too large"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile, HTTPException
    from unittest.mock import MagicMock

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    # Create file larger than 5MB
    large_file_content = b"x" * (6 * 1024 * 1024)
    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.jpg"
    file.file = BytesIO(large_file_content)
    file.content_type = "image/jpeg"

    # Create async read function
    async def async_read():
        return large_file_content
    file.read = async_read

    with patch("app.routes.profile.require_user", return_value=test_user):
        with pytest.raises(HTTPException) as exc_info:
            await upload_avatar(request=request, file=file, session=fake_session)
        assert exc_info.value.status_code == 400


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_success(test_user, fake_session, monkeypatch):
    """Test successful avatar upload"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile
    from unittest.mock import MagicMock

    # Mock S3 client
    mock_s3_client = MagicMock()
    monkeypatch.setattr("app.routes.profile.s3_client", mock_s3_client)

    request = MagicMock()
    request.session = {"user": {"avatar_url": ""}}
    request.headers = {}

    # Create fake image file
    file_content = b"fake image content"
    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.jpg"
    file.file = BytesIO(file_content)
    file.content_type = "image/jpeg"

    # Create async read function
    async def async_read():
        return file_content
    file.read = async_read

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = await upload_avatar(request=request, file=file, session=fake_session)

    # Verify redirect response
    assert result.status_code == 303

    # Verify S3 upload was called
    mock_s3_client.put_object.assert_called_once()
    call_kwargs = mock_s3_client.put_object.call_args[1]
    assert call_kwargs["ContentType"] == "image/jpeg"
    assert str(test_user.id) in call_kwargs["Key"]

    # Verify database update
    updated_user = fake_session.get(User, test_user.id)
    assert updated_user.avatar_url is not None
    assert "avatar" in updated_user.avatar_url


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_s3_error(test_user, fake_session, monkeypatch):
    """Test avatar upload handles S3 errors gracefully"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile
    from botocore.exceptions import ClientError
    from unittest.mock import MagicMock

    # Mock S3 client to raise error
    mock_s3_client = MagicMock()
    mock_s3_client.put_object.side_effect = ClientError(
        {"Error": {"Message": "Access denied"}}, "PutObject"
    )
    monkeypatch.setattr("app.routes.profile.s3_client", mock_s3_client)

    request = MagicMock()
    request.session = {"user": {}}
    request.headers = {}

    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.jpg"
    file.file = BytesIO(b"fake image")
    file.content_type = "image/jpeg"

    # Create async read function
    async def async_read():
        return b"fake image"
    file.read = async_read

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = await upload_avatar(request=request, file=file, session=fake_session)

    # Verify error response
    assert result.status_code == 500


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_png(test_user, fake_session, monkeypatch):
    """Test avatar upload with PNG file"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile
    from unittest.mock import MagicMock

    mock_s3_client = MagicMock()
    monkeypatch.setattr("app.routes.profile.s3_client", mock_s3_client)

    request = MagicMock()
    request.session = {"user": {"avatar_url": ""}}
    request.headers = {}

    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.png"
    file.file = BytesIO(b"fake png")
    file.content_type = "image/png"

    # Create async read function
    async def async_read():
        return b"fake png"
    file.read = async_read

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = await upload_avatar(request=request, file=file, session=fake_session)

    assert result.status_code == 303

    # Verify correct extension
    call_kwargs = mock_s3_client.put_object.call_args[1]
    assert call_kwargs["Key"].endswith(".png")


@pytest.mark.profile
@pytest.mark.asyncio
async def test_upload_avatar_webp(test_user, fake_session, monkeypatch):
    """Test avatar upload with WebP file"""
    from app.routes.profile import upload_avatar
    from fastapi import UploadFile
    from unittest.mock import MagicMock

    mock_s3_client = MagicMock()
    monkeypatch.setattr("app.routes.profile.s3_client", mock_s3_client)

    request = MagicMock()
    request.session = {"user": {"avatar_url": ""}}
    request.headers = {}

    file = MagicMock(spec=UploadFile)
    file.filename = "avatar.webp"
    file.file = BytesIO(b"fake webp")
    file.content_type = "image/webp"

    # Create async read function
    async def async_read():
        return b"fake webp"
    file.read = async_read

    with patch("app.routes.profile.require_user", return_value=test_user):
        result = await upload_avatar(request=request, file=file, session=fake_session)

    assert result.status_code == 303

    # Verify correct extension
    call_kwargs = mock_s3_client.put_object.call_args[1]
    assert call_kwargs["Key"].endswith(".webp")
