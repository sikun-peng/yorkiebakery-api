from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from app.core.db import engine
from app.routes import auth, menu, order, ai, cart, music
from fastapi import Request
from app.core.cart_utils import get_cart_count

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(ai.router)
app.include_router(cart.router)

app.include_router(music.router)

app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_DO_NOT_HARD_CODE")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def home(request: Request):
    cart_count = get_cart_count(request)
    return templates.TemplateResponse("index.html", {"request": request, "cart_count": cart_count})