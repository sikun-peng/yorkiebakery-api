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
    user = session.get(User, user_session["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("")
def profile_page(request: Request, session: Session = Depends(get_session)):
    try:
        user = require_user(request, session)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=303)
    # refresh session avatar if missing
    if "user" in request.session:
        request.session["user"]["avatar_url"] = user.avatar_url
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "errors": {}})


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
    redirect_url = request.headers.get("referer") or "/profile"
    return RedirectResponse(url=redirect_url, status_code=303)


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
            },
            status_code=400,
        )
    if len(new_password) < 6:
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "errors": {"password": "Password must be at least 6 characters"},
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
            },
            status_code=400,
        )
    user.password_hash = hash_password(new_password)
    session.add(user)
    session.commit()
    redirect_url = request.headers.get("referer") or "/profile"
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
    key = f"avatar/{user.id}{ext}"

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
    redirect_url = request.headers.get("referer") or "/profile"
    return RedirectResponse(url=redirect_url, status_code=303)
