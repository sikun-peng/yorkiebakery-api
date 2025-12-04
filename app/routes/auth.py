from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from starlette.templating import Jinja2Templates
from starlette.config import Config
from datetime import datetime, timedelta
import secrets

from app.core.db import get_session
from app.core.logger import get_logger

logger = get_logger(__name__)
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_verification_token, verify_email_token
)
from app.core.send_email import (
    send_verification_email,
    send_password_reset_email,
    send_password_changed_email,
)
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
    first_name: str = ""
    last_name: str = ""


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

    # Choose a sensible default destination (prefer redirect_url param, then referer, else home)
    default_redirect = redirect_url or request.query_params.get("redirect_url") or request.headers.get("referer") or "/"

    return templates.TemplateResponse("login.html", {
        "request": request,
        "redirect_url": default_redirect,
        "page_mode": "login",
    })


@router.get("/register")
def register_page(request: Request, redirect_url: str = None):
    """Render a register page that posts to the register_form endpoint."""
    default_redirect = redirect_url or request.query_params.get("redirect_url") or request.headers.get("referer") or "/"
    return templates.TemplateResponse("login.html", {
        "request": request,
        "redirect_url": default_redirect,
        "page_mode": "register",
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
        "avatar_url": user.avatar_url,
    }

    token = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["access_token"] = token

    # Redirect to intended URL or default (always JSON for consistency with AJAX handlers)
    if redirect_url:
        return JSONResponse({"success": True, "redirect": redirect_url})

    referer = request.headers.get("referer")
    if referer and "/auth" not in referer:
        return JSONResponse({"success": True, "redirect": referer})

    return JSONResponse({"success": True, "redirect": "/"})


# --------------------------------------
# Register (modal) - FIXED VERSION
# --------------------------------------
MIN_PASSWORD_LEN = 6
MAX_PASSWORD_LEN = 32


@router.post("/register_form")
def register_form(
        request: Request,
        email: EmailStr = Form(...),
        password: str = Form(...),
        first_name: str = Form("", description="Optional first name"),
        last_name: str = Form("", description="Optional last name"),
        honeypot: str = Form("", alias="register_contact"),
        form_started_at: str = Form("", alias="register_started_at"),
        session: Session = Depends(get_session),
):
    # Basic anti-bot: honeypot + minimum fill time (2s)
    if honeypot.strip():
        return JSONResponse({"success": False, "error": "Invalid submission."}, status_code=400)
    started = None
    try:
        if form_started_at:
            started = float(form_started_at)
    except Exception:
        started = None
    now_ts = datetime.utcnow().timestamp()
    if started is not None:
        if (now_ts - started) < 2:
            return JSONResponse({"success": False, "error": "Please slow down and try again."}, status_code=400)

    if session.exec(select(User).where(User.email == email)).first():
        return JSONResponse({"success": False, "error": "Email already exists."}, status_code=400)

    if len(password) < MIN_PASSWORD_LEN or len(password) > MAX_PASSWORD_LEN:
        return JSONResponse(
            {"success": False, "error": f"Password must be {MIN_PASSWORD_LEN}-{MAX_PASSWORD_LEN} characters."},
            status_code=400,
        )

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

    logger.debug(f"Sending verification email to {user.email}")
    logger.debug(f"Verification URL: {verify_url}")

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

        logger.debug(f"Resending verification email to {user.email}")
        logger.debug(f"Verification URL: {verify_url}")

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
        "avatar_url": user.avatar_url,
    }

    token_jwt = create_access_token({"sub": str(user.id), "email": user.email})
    request.session["access_token"] = token_jwt

    referer = request.headers.get("referer")
    if referer and "/auth" not in referer:
        return RedirectResponse(referer, status_code=303)
    return RedirectResponse("/", status_code=303)


# --------------------------------------
# Logout
# --------------------------------------
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    referer = request.headers.get("referer")
    target = referer if referer and "/auth" not in referer else "/"
    return RedirectResponse(target, status_code=303)


# --------------------------------------
# JSON Register - FIXED VERSION
# --------------------------------------
@router.post("/register")
def api_register(payload: UserRegisterRequest, session: Session = Depends(get_session), request: Request = None):
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if len(payload.password) < MIN_PASSWORD_LEN or len(payload.password) > MAX_PASSWORD_LEN:
        raise HTTPException(status_code=400, detail=f"Password must be {MIN_PASSWORD_LEN}-{MAX_PASSWORD_LEN} characters.")

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
        "avatar_url": user.avatar_url,
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

    # Remember where to return after OAuth
    redirect_target = request.query_params.get("redirect_url") or request.headers.get("referer") or "/"
    request.session["post_login_redirect"] = redirect_target

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
        "avatar_url": user.avatar_url,
    }
    request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})

    target = request.session.pop("post_login_redirect", None)
    if target and "/auth" not in target:
        return RedirectResponse(target, status_code=303)
    return RedirectResponse("/", status_code=303)


# --------------------------------------
# Facebook OAuth - ADDED MISSING ROUTES
# --------------------------------------
@router.get("/login/facebook")
async def login_facebook(request: Request):
    if not oauth or not getattr(oauth, "facebook", None) or not oauth.facebook.client_id:
        raise HTTPException(status_code=400, detail="Facebook OAuth not configured")

    redirect_target = request.query_params.get("redirect_url") or request.headers.get("referer") or "/"
    request.session["post_login_redirect"] = redirect_target

    redirect_uri = request.url_for("facebook_callback")
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get("/facebook/callback")
async def facebook_callback(request: Request, session: Session = Depends(get_session)):
    # Handle user cancellation or errors from Facebook
    if request.query_params.get("error"):
        target = request.session.pop("post_login_redirect", None)
        if target and "/auth" not in target:
            return RedirectResponse(target, status_code=303)
        return RedirectResponse("/auth/login", status_code=303)

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

        logger.debug(f"Facebook user - ID: {facebook_id}, Name: {first_name} {last_name}")

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
            logger.debug(f"Created new Facebook user: {user.email}")
        else:
            if not user.is_verified:
                user.is_verified = True
                session.add(user)
                session.commit()
            logger.debug(f"Existing Facebook user: {user.email}")

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
            "avatar_url": user.avatar_url,
        }
        request.session["access_token"] = create_access_token({"sub": str(user.id), "email": user.email})

        logger.info(f"Facebook login successful for {user.email}")
        target = request.session.pop("post_login_redirect", None)
        if target and "/auth" not in target:
            return RedirectResponse(target, status_code=303)
        return RedirectResponse("/", status_code=303)

    except Exception as e:
        logger.error(f"Facebook OAuth error: {e}", exc_info=True)
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

        logger.debug(f"Password reset requested for: {email}")

        user = session.exec(select(User).where(User.email == email)).first()

        if user:
            logger.debug(f"User found: {user.email}")

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
            logger.debug("Reset token created and committed to database")

            # Create reset URL
            reset_url = absolute_url(request, f"/auth/reset_password?token={reset_token}")
            logger.debug(f"Reset URL: {reset_url}")

            # Send email
            try:
                send_password_reset_email(user.email, reset_url)
                logger.info(f"Password reset email sent to {user.email}")
            except Exception as email_error:
                logger.warning(f"Failed to send email: {email_error}")
                # Don't fail the request if email fails

        else:
            logger.debug(f"User not found for email: {email}")

        # Always return success to prevent email enumeration
        return JSONResponse({
            "success": True,
            "message": "If an account exists with this email, a reset link has been sent."
        })

    except Exception as e:
        logger.error(f"Error in forgot_password: {e}", exc_info=True)

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
        logger.error(f"Error in reset_password_page: {e}", exc_info=True)
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
        logger.debug(f"Password reset attempt with token: {token}")

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
            logger.warning("Invalid or expired reset token")
            return JSONResponse({
                "success": False,
                "error": "Invalid or expired reset link. Please request a new password reset."
            }, status_code=400)

        # Get user
        user = session.get(User, reset_token_record.user_id)
        if not user:
            logger.warning("User not found for reset token")
            return JSONResponse({
                "success": False,
                "error": "User not found."
            }, status_code=404)

        logger.info(f"Resetting password for user: {user.email}")

        if len(new_password) < MIN_PASSWORD_LEN or len(new_password) > MAX_PASSWORD_LEN:
            return JSONResponse(
                {"success": False, "error": f"Password must be {MIN_PASSWORD_LEN}-{MAX_PASSWORD_LEN} characters."},
                status_code=400,
            )

        # Update password
        user.password_hash = hash_password(new_password)

        # Mark token as used
        reset_token_record.is_used = True

        session.add(user)
        session.add(reset_token_record)
        session.commit()

        logger.info("Password reset successful")

        # Send confirmation email (best-effort)
        try:
            logger.info(f"Sending password-changed email to {user.email}")
            send_password_changed_email(user.email, user.first_name)
        except Exception as email_error:
            logger.warning(f"Failed to send password change email: {email_error}")

        # Return HTML response that shows success and redirects
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "success": True,
            "message": "Password updated successfully! You can now login with your new password."
        })

    except Exception as e:
        logger.error(f"Error in reset_password: {e}", exc_info=True)
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

    logger.info(f"Attempting to send test email to {test_email}")
    logger.debug(f"Reset URL would be: {test_url}")

    try:
        send_password_reset_email(test_email, test_url)
        return {"status": "Email sent successfully", "to": test_email}
    except Exception as e:
        logger.error(f"Test email error: {e}", exc_info=True)
        return {"status": "Email failed", "error": str(e)}
