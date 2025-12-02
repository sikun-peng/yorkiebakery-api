import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from app.core.db import get_session
from app.core.security import verify_password, hash_password
from app.models.postgres.user import User
from fastapi.templating import Jinja2Templates
from botocore.exceptions import BotoCoreError, ClientError
from app.core.logger import get_logger
from app.core.send_email import send_password_changed_email
import boto3
import uuid

router = APIRouter(prefix="/profile", tags=["Profile"])
templates = Jinja2Templates(directory="app/templates")
logger = get_logger(__name__)

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
S3_BUCKET_IMAGE = os.getenv("S3_BUCKET_IMAGE", "yorkiebakery-image")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
# CDN base for serving images; fall back to direct S3 URL
AVATAR_BASE_URL = os.getenv("IMAGE_CDN_BASE", f"https://{S3_BUCKET_IMAGE}.s3.{AWS_REGION}.amazonaws.com")
s3_client = boto3.client("s3", region_name=AWS_REGION)


def require_user(request: Request, session: Session) -> User:
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(status_code=401, detail="Login required")
    user_id = user_session.get("id")
    try:
        from uuid import UUID
        user_id = UUID(str(user_id))
    except Exception:
        pass
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def address_form_values(user: User) -> dict:
    """Provide default values for the address form inputs."""
    return {
        "address_line1": user.address_line1 or "",
        "address_line2": user.address_line2 or "",
        "city": user.city or "",
        "state": user.state or "",
        "postal_code": user.postal_code or "",
        "country": user.country or "",
        "default_phone": user.default_phone or "",
    }


@router.get("")
def profile_page(request: Request, session: Session = Depends(get_session)):
    try:
        user = require_user(request, session)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=303)
    # refresh session avatar if missing
    if "user" in request.session:
        request.session["user"]["avatar_url"] = user.avatar_url
    success = request.query_params.get("success")
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "errors": {},
            "address_values": address_form_values(user),
            "success": success,
        },
    )


# Graceful redirects for GET on POST endpoints
@router.get("/password")
def redirect_password():
    return RedirectResponse(url="/profile", status_code=303)


@router.get("/name")
def redirect_name():
    return RedirectResponse(url="/profile", status_code=303)


@router.get("/avatar")
def redirect_avatar():
    return RedirectResponse(url="/profile", status_code=303)


@router.post("/name")
def update_name(
    request: Request,
    first_name: str = Form(""),
    last_name: str = Form(""),
    session: Session = Depends(get_session),
):
    user = require_user(request, session)
    user.first_name = first_name.strip() or None
    user.last_name = last_name.strip() or None
    session.add(user)
    session.commit()
    # refresh session display name
    request.session["user"]["first_name"] = user.first_name or ""
    redirect_url = "/profile?success=name"
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/address")
def update_address(
    request: Request,
    address_line1: str = Form(""),
    address_line2: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    postal_code: str = Form(""),
    country: str = Form(""),
    default_phone: str = Form(""),
    session: Session = Depends(get_session),
):
    user = require_user(request, session)

    def clean(value: str):
        return value.strip() or None

    cleaned_address = {
        "address_line1": clean(address_line1),
        "address_line2": clean(address_line2),
        "city": clean(city),
        "state": clean(state),
        "postal_code": clean(postal_code),
        "country": clean(country),
        "default_phone": clean(default_phone),
    }

    required_fields = [
        cleaned_address["address_line1"],
        cleaned_address["city"],
        cleaned_address["state"],
        cleaned_address["postal_code"],
        cleaned_address["country"],
    ]

    # Allow clearing the saved address entirely
    if not any(required_fields) and not cleaned_address["address_line2"] and not cleaned_address["default_phone"]:
        user.address_line1 = None
        user.address_line2 = None
        user.city = None
        user.state = None
        user.postal_code = None
        user.country = None
        user.default_phone = None
        session.add(user)
        session.commit()
        return RedirectResponse(url="/profile?success=address", status_code=303)

    if any(required_fields) and not all(required_fields):
        errors = {"address": "Please fill street, city, state, postal code, and country to save your default address."}
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": errors,
                "address_values": {
                    **address_form_values(user),
                    **{k: v or "" for k, v in cleaned_address.items()},
                },
            },
            status_code=400,
        )

    user.address_line1 = cleaned_address["address_line1"]
    user.address_line2 = cleaned_address["address_line2"]
    user.city = cleaned_address["city"]
    user.state = cleaned_address["state"]
    user.postal_code = cleaned_address["postal_code"]
    user.country = cleaned_address["country"]
    user.default_phone = cleaned_address["default_phone"]
    session.add(user)
    session.commit()

    return RedirectResponse(url="/profile?success=address", status_code=303)


@router.post("/password")
def update_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = require_user(request, session)
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": {"password": "Passwords do not match"},
                "address_values": address_form_values(user),
            },
            status_code=400,
        )
    if len(new_password) < 6 or len(new_password) > 32:
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": {"password": "Password must be 6-32 characters"},
                "address_values": address_form_values(user),
            },
            status_code=400,
        )
    if not verify_password(current_password, user.password_hash):
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": {"password": "Current password is incorrect"},
                "address_values": address_form_values(user),
            },
            status_code=400,
        )
    user.password_hash = hash_password(new_password)
    session.add(user)
    session.commit()

    # Best-effort confirmation email
    try:
        logger.info(f"Sending password-changed email to {user.email}")
        send_password_changed_email(user.email, user.first_name)
    except Exception as e:
        logger.warning(f"Failed to send password change email: {e}")

    redirect_url = "/profile?success=password"
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    user = require_user(request, session)

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    ext = ".jpg" if file.content_type == "image/jpeg" else ".png" if file.content_type == "image/png" else ".webp"
    # Use a unique key per upload to bust CDN/browser cache when changing avatars.
    key = f"avatar/{user.id}/{uuid.uuid4()}{ext}"

    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_IMAGE,
            Key=key,
            Body=data,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f"Avatar upload failed: {e}", exc_info=True)
        err_msg = "Failed to upload avatar."
        if isinstance(e, ClientError):
            err_msg += f" ({e.response.get('Error', {}).get('Message', '').strip()})"
        # Return profile page with an error
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": {"avatar": err_msg},
                "address_values": address_form_values(user),
            },
            status_code=500,
        )

    user.avatar_url = f"{AVATAR_BASE_URL}/{key}"
    session.add(user)
    session.commit()

    # update session avatar
    if "user" in request.session:
        request.session["user"]["avatar_url"] = user.avatar_url

    # keep session name intact
    redirect_url = "/profile?success=avatar"
    return RedirectResponse(url=redirect_url, status_code=303)
