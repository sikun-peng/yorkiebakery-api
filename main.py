from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel

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
# Docker copies built React app into: /app/ai_demo_frontend/dist
app.mount(
    "/ai-demo",
    StaticFiles(directory="ai_demo_frontend/dist", html=True),
    name="ai-demo"
)

# Explicit index path (optional but good to have)
@app.get("/ai-demo/index")
def serve_ai_demo_index():
    return FileResponse("ai_demo_frontend/dist/index.html")


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