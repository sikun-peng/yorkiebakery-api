from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel
import os

# Internal imports
from app.core.db import engine
from app.core.cart_utils import get_cart_count
from app.routes import auth, menu, order, cart, music
from app.ai.route import ai_demo, ai_chat, ai_vision, ai_debug

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

# Serve other static files that might be in dist root
@app.get("/{filename}")
async def serve_root_files(filename: str):
    file_path = os.path.join(frontend_dist_path, filename)
    if os.path.exists(file_path) and filename != "index.html":
        return FileResponse(file_path)
    # Let the mount handle index.html and other routes

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

# AI / RAG routers
app.include_router(ai_demo.router)
app.include_router(ai_chat.router)
app.include_router(ai_vision.router)
app.include_router(ai_debug.router)

# ===============================================
# HOME PAGE
# ===============================================
@app.get("/")
def home(request: Request):
    cart_count = get_cart_count(request)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "cart_count": cart_count}
    )