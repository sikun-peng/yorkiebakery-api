# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer
from fastapi import HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext
import os
import secrets


# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- JWT (still useful for API/mobile, optional for web) ---
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SERIALIZER = URLSafeTimedSerializer(SECRET_KEY)

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# --- Session helpers for web pages ---
def get_session_user(request: Request) -> Optional[dict]:
    # We only store a small, safe subset in the session
    return request.session.get("user")

def require_logged_in(request: Request) -> dict:
    user = get_session_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )
    return user

def require_admin(request: Request) -> dict:
    user = require_logged_in(request)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def create_verification_token(email: str):
    return SERIALIZER.dumps(email, salt="email-verify")

def verify_email_token(token: str, max_age=3600):
    from itsdangerous import SignatureExpired, BadSignature
    try:
        email = SERIALIZER.loads(token, salt="email-verify", max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None

def create_password_reset_token() -> str:
    """Create a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def verify_password_reset_token(token: str) -> str | None:
    """Verify password reset token (you'll need to check database)"""
    # This just validates format, actual verification happens in database
    if len(token) >= 32:  # Basic validation
        return token
    return None