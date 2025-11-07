from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.db import engine
from app.routes import auth, menu, order, ai
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Serve static JS/CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(ai.router)

# Session middleware
app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)