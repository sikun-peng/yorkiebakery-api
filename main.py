from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.db import engine
from app.routes import auth, menu, order
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(order.router)

app.add_middleware(SessionMiddleware, secret_key="YOUR_SECRET_KEY")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)