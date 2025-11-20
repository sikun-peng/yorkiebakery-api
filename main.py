from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from app.ai.route import ai_demo, ai_chat, ai_vision, ai_debug
from app.core.db import engine
from app.routes import auth, menu, order, cart, music

from fastapi import Request
from app.core.cart_utils import get_cart_count
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.router.default_options = True

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(cart.router)
app.include_router(music.router)
app.include_router(ai_demo.router)
app.include_router(ai_chat.router)
app.include_router(ai_vision.router)
app.include_router(ai_debug.router)

app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_DO_NOT_HARD_CODE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"]
    allow_credentials=True,
    allow_methods=["*"],  # <---- IMPORTANT
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def home(request: Request):
    cart_count = get_cart_count(request)
    return templates.TemplateResponse("index.html", {"request": request, "cart_count": cart_count})

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount(
    "/ai-demo-assets",
    StaticFiles(directory="ai_demo_frontend/dist/assets"),
    name="ai_demo_assets"
)

@app.get("/ai-demo")
def serve_ai_demo():
    return FileResponse("ai_demo_frontend/dist/index.html")