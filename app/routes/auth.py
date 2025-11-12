# app/routes/auth.py

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from starlette.templating import Jinja2Templates
from starlette.config import Config

from app.core.db import get_session
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_verification_token, verify_email_token
)
from app.core.send_email import send_verification_email
from app.models.postgres.user import User

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------------------
# OAuth (optional; only if set)
# -----------------------------
try:
    from authlib.integrations.starlette_client import OAuth
    config = Config(".env")
    oauth = OAuth(config)

    # Google OAuth
    oauth.register(
        name="google",
        client_id=config("GOOGLE_CLIENT_ID", default=None),
        client_secret=config("GOOGLE_CLIENT_SECRET", default=None),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # Facebook OAuth (kept for parity; unused unless keys set)
    oauth.register(
        name="facebook",
        client_id=config("FACEBOOK_CLIENT_ID", default=None),
        client_secret=config("FACEBOOK_CLIENT_SECRET", default=None),
        access_token_url="https://graph.facebook.com/v12.0/oauth/access_token",
        authorize_url="https://www.facebook.com/v12.0/dialog/oauth",
        api_base_url="https://graph.facebook.com/v12.0/",
        client_kwargs={"scope": "email public_profile"},
    )
except Exception:
    oauth = None


# -----------------------------
# Request models (API JSON)
# -----------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


# ------------------------------------------------
# Optional: legacy login page (your UI uses modal)
# ------------------------------------------------
@router.get("/login")
def login_page(_: Request):
    # We don't render login.html anymore—modal handles UI.
    return JSONResponse({"detail": "Use the in-page login modal."})


# --------------------------------------
# Login (modal POST -> returns JSON)
# --------------------------------------
@router.post("/login_form")
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return JSONResponse({"success": False, "error": "Invalid email or password."}, status_code=400)

    # if not user.is_verified:
        # return JSONResponse({"success": False, "error": "Please verify your email first."}, status_code=403)

    # Session + JWT
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    token = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["access_token"] = token

    return JSONResponse({"success": True})


# --------------------------------------
# Register (modal POST -> returns JSON)
# --------------------------------------
@router.post("/register_form")
def register_form(
    request: Request,
    email: EmailStr = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    session: Session = Depends(get_session),
):
    if session.exec(select(User).where(User.email == email)).first():
        return JSONResponse({"success": False, "error": "Email already exists."}, status_code=400)

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=hash_password(password),
        is_verified=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Send verification email
    token = create_verification_token(user.email)
    verify_link = f"{request.url_for('verify_email')}?token={token}"
    #TODO:  send_verification_email(user.email, verify_link)

    # Do NOT log them in yet; require verification first
    return JSONResponse({"success": True, "message": "Check your email to verify your account."})


# --------------------------------------
# Resend verification (optional helper)
# --------------------------------------
@router.post("/resend_verification")
def resend_verification(
    request: Request,
    email: EmailStr = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()
    # Always respond success to avoid user enumeration
    if user and not user.is_verified:
        token = create_verification_token(user.email)
        verify_link = f"{request.url_for('verify_email')}?token={token}"
        #TODO: send_verification_email(user.email, verify_link)
    return JSONResponse({"success": True, "message": "If this email exists and is unverified, a new link was sent."})


# --------------------------------------
# Verify email link
# --------------------------------------
@router.get("/verify", name="verify_email")
def verify_email(request: Request, token: str, session: Session = Depends(get_session)):
    email = verify_email_token(token)
    if not email:
        return JSONResponse({"success": False, "error": "Verification link expired or invalid."}, status_code=400)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return JSONResponse({"success": False, "error": "User not found."}, status_code=404)

    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        session.commit()

    # Auto-login after verification
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    token_jwt = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["access_token"] = token_jwt

    return RedirectResponse("/menu/view", status_code=303)


# --------------------------------------
# Logout
# --------------------------------------
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/menu/view", status_code=303)


# --------------------------------------
# JSON API: register (programmatic)
# --------------------------------------
@router.post("/register")
def api_register(payload: UserRegisterRequest, session: Session = Depends(get_session), request: Request = None):
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hash_password(payload.password),
        is_verified=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # send verification email
    if request is not None:
        token = create_verification_token(user.email)
        verify_link = f"{request.url_for('verify_email')}?token={token}"
        #TODO: send_verification_email(user.email, verify_link)

    return {"msg": "User created. Please verify your email.", "user_id": str(user.id)}


# --------------------------------------
# JSON API: login (programmatic)
# --------------------------------------
@router.post("/login")
def api_login(payload: UserLoginRequest, request: Request, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token = create_access_token({"sub": str(user.id), "email": user.email})

    # Fill session too (useful for hybrid API/browser)
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = token

    return {"access_token": token, "token_type": "bearer"}


# --------------------------------------
# Google OAuth (marks users verified)
# --------------------------------------
@router.get("/login/google")
async def login_google(request: Request):
    if not oauth or not getattr(oauth, "google", None) or not oauth.google.client_id:
        raise HTTPException(status_code=400, detail="Google OAuth is not configured")
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo") or {}

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email")

    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        # Create verified user from provider identity
        placeholder_pw = hash_password("oauth-user")
        user = User(
            email=email,
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            password_hash=placeholder_pw,
            is_verified=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # If existing local account wasn't verified yet, trust Google to verify email ownership
        if not user.is_verified:
            user.is_verified = True
            session.add(user)
            session.commit()

    # Start session
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})
    return RedirectResponse(url="/menu/view", status_code=303)