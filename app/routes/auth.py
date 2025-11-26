from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from starlette.templating import Jinja2Templates
from starlette.config import Config
from datetime import datetime, timedelta
import secrets

from app.core.db import get_session
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_verification_token, verify_email_token
)
from app.core.send_email import send_verification_email, send_password_reset_email
from app.models.postgres.user import User
from app.models.postgres.password_reset_token import PasswordResetToken

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["Auth"])


# --------------------------------------
# FIXED: Helper for correct absolute URLs
# --------------------------------------
def absolute_url(request: Request, path: str = "") -> str:
    """Create absolute URL safely"""
    base = str(request.base_url).rstrip("/")
    if path.startswith("/"):
        path = path[1:]
    return f"{base}/{path}"


# --------------------------------------
# Password Reset Token Functions
# --------------------------------------
def create_password_reset_token() -> str:
    """Create a secure random token for password reset"""
    return secrets.token_urlsafe(32)


# --------------------------------------
# OAuth (optional)
# --------------------------------------
try:
    from authlib.integrations.starlette_client import OAuth

    config = Config(".env")
    oauth = OAuth(config)

    oauth.register(
        name="google",
        client_id=config("GOOGLE_CLIENT_ID", default=None),
        client_secret=config("GOOGLE_CLIENT_SECRET", default=None),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    oauth.register(
        name="facebook",
        client_id=config("FACEBOOK_CLIENT_ID", default=None),
        client_secret=config("FACEBOOK_CLIENT_SECRET", default=None),
        access_token_url="https://graph.facebook.com/v12.0/oauth/access_token",
        authorize_url="https://www.facebook.com/v12.0/dialog/oauth",
        api_base_url="https://graph.facebook.com/v12.0/",
        client_kwargs={"scope": "public_profile"},  # Only public_profile, no email
    )

except Exception:
    oauth = None


# --------------------------------------
# Request Models
# --------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


# --------------------------------------
# Login endpoint
# --------------------------------------
@router.get("/login")
def login_page(request: Request, redirect_url: str = None):
    """Handle both modal and page-based login"""
    # If it's an API request or AJAX, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JSONResponse({"detail": "Use the in-page login modal."})

    # If it's a redirect from checkout, show login page
    return templates.TemplateResponse("login.html", {
        "request": request,
        "redirect_url": redirect_url or "/menu/view"
    })

# --------------------------------------
# Login (modal -> JSON)
# --------------------------------------
@router.post("/login_form")
def login_form(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        redirect_url: str = Form(None),  # Add redirect parameter
        session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return JSONResponse({"success": False, "error": "Invalid email or password."}, status_code=400)

    if not user.is_verified:
        return JSONResponse({
            "success": False,
            "error": "Please verify your email before logging in. Check your inbox for the verification link."
        }, status_code=403)

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    # Set session
    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }

    token = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["access_token"] = token

    # Redirect to intended URL or default
    if redirect_url:
        return RedirectResponse(redirect_url, status_code=303)

    return JSONResponse({"success": True, "redirect": "/cart/checkout"})


# --------------------------------------
# Register (modal) - FIXED VERSION
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

    token = create_verification_token(user.email)
    verify_url = absolute_url(request, f"/auth/verify?token={token}")

    print(f"DEBUG: Sending verification email to {user.email}")
    print(f"DEBUG: Verification URL: {verify_url}")

    send_verification_email(user.email, verify_url)

    return JSONResponse({"success": True, "message": "Check your email to verify your account."})


# --------------------------------------
# Resend verification (modal) - FIXED VERSION
# --------------------------------------
@router.post("/resend_verification")
def resend_verification(
        request: Request,
        email: EmailStr = Form(...),
        session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()

    if user and not user.is_verified:
        # FIXED: Proper URL construction
        token = create_verification_token(user.email)
        verify_url = absolute_url(request, f"/auth/verify?token={token}")

        print(f"DEBUG: Resending verification email to {user.email}")
        print(f"DEBUG: Verification URL: {verify_url}")

        send_verification_email(user.email, verify_url)

    return JSONResponse({"success": True})


# --------------------------------------
# Email verification handler
# --------------------------------------
@router.get("/verify", name="verify_email")
def verify_email(request: Request, token: str, session: Session = Depends(get_session)):
    email = verify_email_token(token)
    if not email:
        return JSONResponse({"success": False, "error": "Verification link invalid or expired."}, status_code=400)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return JSONResponse({"success": False, "error": "User not found"}, status_code=404)

    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        session.commit()

    # Auto-login
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
    return RedirectResponse("/menu/view", status_code=303)


# --------------------------------------
# JSON Register - FIXED VERSION
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

    if request:
        # FIXED: Proper URL construction
        token = create_verification_token(user.email)
        verify_url = absolute_url(request, f"/auth/verify?token={token}")
        send_verification_email(user.email, verify_url)

    return {"msg": "User created. Please verify email.", "user_id": str(user.id)}


# --------------------------------------
# JSON Login
# --------------------------------------
@router.post("/login")
def api_login(payload: UserLoginRequest, request: Request, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email})

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
# Google OAuth
# --------------------------------------
@router.get("/login/google")
async def login_google(request: Request):
    if not oauth or not getattr(oauth, "google", None) or not oauth.google.client_id:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")

    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo") or {}

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google did not return email")

    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
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
        if not user.is_verified:
            user.is_verified = True
            session.add(user)
            session.commit()

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    request.session["user"] = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": bool(user.is_admin),
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})

    return RedirectResponse("/menu/view", status_code=303)


# --------------------------------------
# Facebook OAuth - ADDED MISSING ROUTES
# --------------------------------------
@router.get("/login/facebook")
async def login_facebook(request: Request):
    if not oauth or not getattr(oauth, "facebook", None) or not oauth.facebook.client_id:
        raise HTTPException(status_code=400, detail="Facebook OAuth not configured")

    redirect_uri = request.url_for("facebook_callback")
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get("/facebook/callback")
async def facebook_callback(request: Request, session: Session = Depends(get_session)):
    try:
        token = await oauth.facebook.authorize_access_token(request)

        # Get user info from Facebook - only public_profile (no email without review)
        resp = await oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,first_name,last_name',
                                        token=token)
        user_info = resp.json()

        # Create a placeholder email using Facebook ID
        facebook_id = user_info.get('id')
        if not facebook_id:
            raise HTTPException(status_code=400, detail="Facebook did not return user ID")

        # Generate unique email from Facebook ID
        email = f"fb_{facebook_id}@facebook.user"

        # Extract names from Facebook data
        first_name = user_info.get('first_name') or 'Facebook'
        last_name = user_info.get('last_name') or 'User'

        # If no first/last name, try to parse from full name
        if first_name == 'Facebook':
            name_parts = user_info.get('name', '').split(' ', 1)
            if name_parts:
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else 'User'

        print(f"DEBUG: Facebook user - ID: {facebook_id}, Name: {first_name} {last_name}")

        # Check if user already exists
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            placeholder_pw = hash_password("oauth-user")
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password_hash=placeholder_pw,
                is_verified=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"DEBUG: Created new Facebook user: {user.email}")
        else:
            if not user.is_verified:
                user.is_verified = True
                session.add(user)
                session.commit()
            print(f"DEBUG: Existing Facebook user: {user.email}")

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        session.add(user)
        session.commit()

        # Set session
        request.session["user"] = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": bool(user.is_admin),
        }
        request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})

        print(f"DEBUG: Facebook login successful for {user.email}")
        return RedirectResponse("/menu/view", status_code=303)

    except Exception as e:
        print(f"Facebook OAuth error: {e}")
        # More detailed error logging
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail="Facebook login failed")


# --------------------------------------
# Forgot Password - FIXED VERSION
# --------------------------------------
@router.post("/forgot_password")
async def forgot_password(
        request: Request,
        session: Session = Depends(get_session)
):
    try:
        data = await request.json()
        email = data.get('email')

        if not email:
            return JSONResponse(
                {"success": False, "error": "Email is required"},
                status_code=400
            )

        print(f"DEBUG: Password reset requested for: {email}")

        user = session.exec(select(User).where(User.email == email)).first()

        if user:
            print(f"DEBUG: User found: {user.email}")

            # Create secure reset token
            reset_token = create_password_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Create reset token record
            reset_token_record = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at
            )

            session.add(reset_token_record)
            session.commit()  # ✅ CRITICAL: COMMIT THE TRANSACTION
            print(f"DEBUG: Reset token created and committed to database")

            # Create reset URL
            reset_url = absolute_url(request, f"/auth/reset_password?token={reset_token}")
            print(f"DEBUG: Reset URL: {reset_url}")

            # Send email
            try:
                send_password_reset_email(user.email, reset_url)
                print(f"DEBUG: Password reset email sent to {user.email}")
            except Exception as email_error:
                print(f"DEBUG: Failed to send email: {email_error}")
                # Don't fail the request if email fails

        else:
            print(f"DEBUG: User not found for email: {email}")

        # Always return success to prevent email enumeration
        return JSONResponse({
            "success": True,
            "message": "If an account exists with this email, a reset link has been sent."
        })

    except Exception as e:
        print(f"DEBUG: Error in forgot_password: {e}")
        # Log the full error for debugging
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")

        session.rollback()
        return JSONResponse({
            "success": True,  # Still return success for security
            "message": "If an account exists with this email, a reset link has been sent."
        })


# --------------------------------------
# Reset Password Page - FIXED VERSION
# --------------------------------------
# --------------------------------------
# Reset Password Page - FIXED VERSION
# --------------------------------------
@router.get("/reset_password")
def reset_password_page(
        request: Request,
        token: str,
        session: Session = Depends(get_session)  # ✅ ADD THIS DEPENDENCY
):
    # Basic token validation
    if not token or len(token) < 10:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": "Invalid reset token."
        })

    # Verify token is valid in database
    try:
        reset_token_record = session.exec(
            select(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .where(PasswordResetToken.is_used == False)
            .where(PasswordResetToken.expires_at > datetime.utcnow())
        ).first()

        if not reset_token_record:
            return templates.TemplateResponse("reset_password.html", {
                "request": request,
                "token": token,
                "error": "Invalid or expired reset link. Please request a new password reset."
            })

        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": None
        })
    except Exception as e:
        print(f"DEBUG: Error in reset_password_page: {e}")
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": "Error validating reset token."
        })



# --------------------------------------
# Process Password Reset - FIXED VERSION
# --------------------------------------
# --------------------------------------
# Process Password Reset - FIXED VERSION
# --------------------------------------
@router.post("/reset_password")
async def reset_password(
        request: Request,
        token: str = Form(...),
        new_password: str = Form(...),
        session: Session = Depends(get_session)
):
    try:
        print(f"DEBUG: Password reset attempt with token: {token}")

        if not token or len(token) < 10:
            return JSONResponse({
                "success": False,
                "error": "Invalid reset token."
            }, status_code=400)

        # Find valid reset token
        reset_token_record = session.exec(
            select(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .where(PasswordResetToken.is_used == False)
            .where(PasswordResetToken.expires_at > datetime.utcnow())
        ).first()

        if not reset_token_record:
            print("DEBUG: Invalid or expired reset token")
            return JSONResponse({
                "success": False,
                "error": "Invalid or expired reset link. Please request a new password reset."
            }, status_code=400)

        # Get user
        user = session.get(User, reset_token_record.user_id)
        if not user:
            print("DEBUG: User not found for reset token")
            return JSONResponse({
                "success": False,
                "error": "User not found."
            }, status_code=404)

        print(f"DEBUG: Resetting password for user: {user.email}")

        # Update password
        user.password_hash = hash_password(new_password)

        # Mark token as used
        reset_token_record.is_used = True

        session.add(user)
        session.add(reset_token_record)
        session.commit()

        print("DEBUG: Password reset successful")

        # Return HTML response that shows success and redirects
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "success": True,
            "message": "Password updated successfully! You can now login with your new password."
        })

    except Exception as e:
        print(f"DEBUG: Error in reset_password: {e}")
        session.rollback()
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": "An error occurred while resetting your password."
        })


# --------------------------------------
# Debug Endpoints
# --------------------------------------
@router.get("/debug/tables")
async def debug_tables(session: Session = Depends(get_session)):
    """Check if password_reset_token table exists"""
    try:
        # Try to query the table
        result = session.exec(select(PasswordResetToken).limit(1)).first()
        return {"status": "Table exists", "sample": result is not None}
    except Exception as e:
        return {"status": "Table missing", "error": str(e)}


@router.get("/test_email")
async def test_email(request: Request):
    """Test email configuration"""
    test_email = "sikun.peng1990@yahoo.com"
    test_url = absolute_url(request, "/auth/reset_password?token=test123")

    print(f"TEST: Attempting to send email to {test_email}")
    print(f"TEST: Reset URL would be: {test_url}")

    try:
        send_password_reset_email(test_email, test_url)
        return {"status": "Email sent successfully", "to": test_email}
    except Exception as e:
        print(f"TEST EMAIL ERROR: {e}")
        return {"status": "Email failed", "error": str(e)}