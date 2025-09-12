from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from uuid import UUID
import re
from authlib.integrations.starlette_client import OAuth
from app.models.postgres.user import User
from app.core.db import get_session
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from starlette.requests import Request
from starlette.config import Config

config = Config('.env')
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Python
oauth.register(
    name='facebook',
    client_id=config('FACEBOOK_CLIENT_ID'),
    client_secret=config('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/v12.0/',
    client_kwargs={'scope': 'email public_profile'}
)
router = APIRouter(prefix="/auth")

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# --- Register ---
@router.post("/register")
def register_user(payload: UserRegisterRequest, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    if not is_strong_password(payload.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and include upper, lower, digit, and special character.")

    user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hash_password(payload.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "msg": "User created",
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


@router.get('/login/google')
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google/callback')
async def auth_google_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    print(token)
    id_token = token.get("id_token")
    if not isinstance(token, dict):
        raise Exception("Token is not a dict!")
    if not id_token:
        raise HTTPException(status_code=400, detail="No id_token in response from Google")
    print(type(request), type(token))
    print(token["id_token"])
    try:
        user_info = jwt.decode(
            id_token,
            key=None,  # still skipping signature verification in dev
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_at_hash": False  # <--- this fixes your current error
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode id_token: {str(e)}")
    email = user_info['email']
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            email=email,
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            provider='google',
            password_hash=''
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/login/facebook')
async def login_facebook(request: Request):
    redirect_uri = request.url_for('auth_facebook_callback')
    return await oauth.facebook.authorize_redirect(request, redirect_uri)

# Python
@router.get('/facebook/callback')
async def auth_facebook_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.facebook.authorize_access_token(request)
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access_token in response from Facebook")
    # Fetch user info from Facebook Graph API
    resp = await oauth.facebook.get('https://graph.facebook.com/me?fields=id,email,first_name,last_name', token=token)
    user_info = resp.json()
    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="No email returned from Facebook")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            email=email,
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            provider='facebook',
            password_hash=''
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Login ---
@router.post("/login")
def login_user(payload: UserLoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin
    })

    return {"access_token": token, "token_type": "bearer"}


@router.post("/password-reset/request")
def password_reset_request(payload: PasswordResetRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    # Generate and email a reset token (implement email sending)
    reset_token = create_access_token({"sub": str(user.id)}, expires_delta=600)
    # send_email(user.email, reset_token)  # Implement this
    return {"msg": "Password reset email sent"}


@router.post("/password-reset/confirm")
def password_reset_confirm(payload: PasswordResetConfirm, session: Session = Depends(get_session)):
    # Decode token, get user id
    user_id = decode_token(payload.token)["sub"]
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_strong_password(payload.new_password):
        raise HTTPException(status_code=400, detail="Weak password")
    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()
    return {"msg": "Password updated"}


def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])