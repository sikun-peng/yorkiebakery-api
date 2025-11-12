from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime

class MusicTrack(SQLModel, table=True):
    __tablename__ = "music_track"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    composer: str
    performer: str
    category: str
    description: str
    file_url: str
    cover_url: str | None = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)