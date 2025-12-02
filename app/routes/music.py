from fastapi import APIRouter, Request, Form, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.core.db import engine
from app.models.postgres.music import MusicTrack
from app.utils.s3_util import upload_file_to_s3
from app.core.security import require_admin
import os

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/music", tags=["Music"])
S3_BUCKET_MUSIC = os.getenv("S3_BUCKET_MUSIC", "yorkiebakery-music")


# ======================================================
#   Utility: Extract Last Name from Composer Field
# ======================================================
def extract_last_name(composer: str) -> str:
    """
    Extract the last name from a composer string.

    Supports both:
    - "Chopin, Frédéric"
    - "Frédéric Chopin"
    """

    if not composer:
        return ""

    composer = composer.strip()

    # Case 1: "Chopin, Frédéric"
    if "," in composer:
        return composer.split(",")[0].strip()

    # Case 2: "Frédéric Chopin"
    parts = composer.split()
    return parts[-1].strip() if parts else ""


# ===============================
# PUBLIC
# ===============================
@router.get("/listen")
def listen(request: Request):
    """Public-facing page showing all uploaded tracks."""
    with Session(engine) as session:
        tracks = session.exec(select(MusicTrack)).all()

    # ------------------------------------------------------
    # Sort Order:
    # 1. category (raw DB category)
    # 2. composer's last name
    # 3. track title
    # ------------------------------------------------------
    tracks.sort(
        key=lambda t: (
            t.category.lower() if t.category else "",
            extract_last_name(t.composer).lower(),
            t.title.lower() if t.title else "",
        )
    )

    return templates.TemplateResponse(
        "music.html",
        {
            "request": request,
            "tracks": tracks,
            "cart_count": sum(request.session.get("cart", {}).values()),
        },
    )


# ===============================
# ADMIN
# ===============================
@router.get("/new")
def upload_page(request: Request, user=Depends(require_admin)):
    """Render upload form for admin users."""
    return templates.TemplateResponse("music_new.html", {"request": request})


@router.post("/new")
async def upload_track(
        request: Request,
        title: str = Form(...),
        composer: str = Form(...),
        performer: str = Form(...),
        category: str = Form(...),
        description: str = Form(...),
        file: UploadFile = Form(...),
        cover: UploadFile | None = None,
        user=Depends(require_admin),
):
    """Handle new music upload to S3 and save metadata to DB."""

    # --- Validate main audio ---
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are allowed")

    file_url = upload_file_to_s3(file, folder="music", bucket=S3_BUCKET_MUSIC)

    # --- Optional cover image ---
    cover_url = None
    if cover and cover.filename:
        if not cover.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Cover must be an image file")
        cover_url = upload_file_to_s3(cover, folder="music-covers", bucket=S3_BUCKET_MUSIC)

    # --- Save track to DB ---
    with Session(engine) as session:
        track = MusicTrack(
            title=title.strip(),
            composer=composer.strip(),
            performer=performer.strip(),
            category=category.strip(),
            description=description.strip(),
            file_url=file_url,
            cover_url=cover_url,
        )
        session.add(track)
        session.commit()

    return RedirectResponse("/music/listen", status_code=303)
