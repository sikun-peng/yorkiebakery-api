# app/core/db.py
import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from app.core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

logger.info(f"Using DATABASE_URL: {DATABASE_URL}")

if DATABASE_URL.startswith("sqlite"):
    # SQLite (tests/dev) doesn't support the pooling args above
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

def get_session():
    with Session(engine) as session:
        yield session
