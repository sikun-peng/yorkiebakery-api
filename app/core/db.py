# app/core/db.py
from sqlmodel import create_engine, Session
import os

# Docker Postgres container defaults
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/yorkiebakery"
)

# Create the shared engine
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """FastAPI dependency that provides a DB session."""
    with Session(engine) as session:
        yield session