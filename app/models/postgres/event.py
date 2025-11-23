from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid


class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    event_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool = Field(default=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationship
    rsvps: list["EventRSVP"] = Relationship(back_populates="event")


class EventRSVP(SQLModel, table=True):
    __tablename__ = "event_rsvp"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="event.id")
    name: str
    email: str
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event: Optional[Event] = Relationship(back_populates="rsvps")