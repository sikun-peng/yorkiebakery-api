# app/routes/auth.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from starlette.templating import Jinja2Templates
from starlette.config import Config

from app.core.db import get_session
from app.core.security import (
    hash_password, verify_password,
    create_access_token
)
from app.models.postgres.user import User

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["Auth"])

# --- OAuth Setup ---
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

    # Facebook OAuth
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


# --- Request Models ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Login Page ---
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# --- Login Form ---
@router.post("/login_form")
def login_form(request: Request, email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."}, status_code=400)

    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})
    return RedirectResponse(url="/menu/view", status_code=303)


# --- Register Form ---
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
        return templates.TemplateResponse("login.html", {"request": request, "tab": "register", "error": "Email already exists."}, status_code=400)

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})
    return RedirectResponse(url="/menu/view", status_code=303)


# --- Logout ---
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/menu/view", status_code=303)


# --- JSON Login/Register (unchanged) ---
@router.post("/register")
def api_register(payload: UserRegisterRequest, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    return {"msg": "User created", "user_id": str(user.id)}

@router.post("/login")
def api_login(payload: UserLoginRequest, request: Request, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    request.session["access_token"] = token
    return {"access_token": token, "token_type": "bearer"}


# --- Google OAuth ---
@router.get("/login/google")
async def login_google(request: Request):
    if not oauth or not oauth.google.client_id:
        raise HTTPException(status_code=400, detail="Google OAuth is not configured")
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    email = user_info["email"]
    user = session.exec(select(User).where(User.email == email)).first()

    # ✅ Ensure password_hash is never null
    if not user:
        placeholder_pw = hash_password("oauth-user")
        user = User(
            email=email,
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            password_hash=placeholder_pw,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})
    return RedirectResponse(url="/menu/view", status_code=303)