from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, select
from sqlalchemy.sql import func
import os

# Internal imports
from app.core.db import engine
from app.core.db import get_session
from app.core.cart_utils import get_cart_count
from app.models.postgres.menu import MenuItem
from app.models.postgres.music import MusicTrack
from app.models.postgres.review import Review
from app.routes import auth, menu, order, cart, music, about, event, health, review, profile
from app.graphql.schema import graphql_router
from app.ai.route import ai_demo, ai_chat, ai_vision, ai_debug
from app.models.postgres.user import User

# ===============================================
# FASTAPI APP INIT
# ===============================================
app = FastAPI()
app.router.default_options = True

templates = Jinja2Templates(directory="app/templates")

# ===============================================
# STATIC FILES (Backend static assets)
# ===============================================
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ===============================================
# FRONTEND (AI DEMO) STATIC FILES
# ===============================================
frontend_dist_path = "ai_demo_frontend/dist"

# Serve the React app
app.mount(
    "/ai-demo",
    StaticFiles(directory=frontend_dist_path, html=True),
    name="ai-demo"
)

# Serve React static assets from the root path (this fixes the 404 errors)
@app.get("/assets/{filename:path}")
async def serve_react_assets(filename: str):
    asset_path = os.path.join(frontend_dist_path, "assets", filename)
    if os.path.exists(asset_path):
        return FileResponse(asset_path)
    else:
        return {"error": "Asset not found"}, 404

# Catch-all for React Router - serve index.html for any unmatched ai-demo routes
@app.get("/ai-demo/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse(os.path.join(frontend_dist_path, "index.html"))

# Explicit index path
@app.get("/ai-demo")
@app.get("/ai-demo/")
def serve_ai_demo_index():
    return FileResponse(os.path.join(frontend_dist_path, "index.html"))

# ===============================================
# MIDDLEWARE
# ===============================================
app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_DO_NOT_HARD_CODE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://beta.yorkiebakery.com",
        "https://yorkiebakery.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================
# USER CONTEXT MIDDLEWARE (refresh avatar/session)
# ===============================================
@app.middleware("http")
async def attach_user(request: Request, call_next):
    try:
        # short-lived session for user refresh
        for session_db in get_session():
            user_session = request.session.get("user")
            if user_session:
                user_id = user_session.get("id")
                # session stores id as string; cast to UUID for safety
                if user_id:
                    try:
                        from uuid import UUID
                        user_id_obj = UUID(str(user_id))
                    except Exception:
                        user_id_obj = user_id
                else:
                    user_id_obj = None

                user = session_db.get(User, user_id_obj) if user_id_obj else None
                if user:
                    request.state.current_user = user
                    # Keep session data in sync (helps navbar/chat avatar refresh right after login)
                    request.session["user"]["avatar_url"] = user.avatar_url
                    request.session["user"]["first_name"] = user.first_name
                    request.session["user"]["last_name"] = user.last_name
            break
    except Exception:
        pass

    response = await call_next(request)
    return response

# ===============================================
# STARTUP — DB Init
# ===============================================
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ===============================================
# ROUTERS
# ===============================================
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(cart.router)
app.include_router(music.router)
app.include_router(about.router)
app.include_router(event.router)
app.include_router(health.router)
app.include_router(review.router)
app.include_router(profile.router)
app.include_router(graphql_router, prefix="/graphql")

# AI / RAG routers
app.include_router(ai_demo.router)
app.include_router(ai_chat.router)
app.include_router(ai_vision.router)
app.include_router(ai_debug.router)


# ===============================================
# HOME PAGE
# ===============================================
@app.get("/")
def home(request: Request, session=Depends(get_session)):
    cart_count = get_cart_count(request)

    # 🎂 Featured menu — only pastry category AND available items
    menu_items = session.exec(
        select(MenuItem)
        .where(MenuItem.category == "pastry")
        .where(MenuItem.is_available == True)
        .order_by(func.random())
    ).all()

    # Fetch review stats for featured menu items
    review_stats = {}
    menu_ids = [m.id for m in menu_items]
    if menu_ids:
        rows = session.exec(
            select(
                Review.menu_item_id,
                func.count(Review.id),
                func.avg(Review.rating),
            )
            .where(Review.menu_item_id.in_(menu_ids))
            .group_by(Review.menu_item_id)
        ).all()
        for menu_id, count, avg in rows:
            review_stats[str(menu_id)] = {"count": count, "avg": float(avg) if avg is not None else None}

    # 🎵 Featured music — only tracks with audio file (non-null s3_url)
    tracks = session.exec(
        select(MusicTrack)
        .where(MusicTrack.file_url != "")
        .order_by(func.random())
    ).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "cart_count": cart_count,
            "menu_items": menu_items,
            "review_stats": review_stats,
            "tracks": tracks,
        }
    )
