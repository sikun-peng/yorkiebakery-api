# app/routes/event.py

from fastapi import (
    APIRouter, Request, Form, UploadFile, File,
    HTTPException
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from uuid import UUID
import uuid
from datetime import datetime

from app.core.db import engine
from app.core.send_email import send_email
from app.models.postgres.event import Event, EventRSVP
from app.utils.s3_util import upload_file_to_s3

router = APIRouter(prefix="/events", tags=["Events"])
templates = Jinja2Templates(directory="app/templates")


# ======================================================
# Helper — Admin Only
# ======================================================
def require_admin(request: Request):
    user = request.session.get("user")
    if not user or not user.get("is_admin"):
        raise HTTPException(403, "Admin only")
    return user


# ======================================================
# Public: List All Active Events
# ======================================================
@router.get("")
@router.get("/view")
def list_events(request: Request):
    with Session(engine) as session:
        events = session.exec(
            select(Event).where(Event.is_active == True)
        ).all()

    return templates.TemplateResponse(
        "events.html",
        {"request": request, "events": events}
    )


# ======================================================
# Public: Submit RSVP
# ======================================================
@router.post("/rsvp/{event_id}")
def submit_rsvp(
    event_id: UUID,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form("")
):
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(404, "Event not found")

        # 🔥 Extract values BEFORE session closes
        event_title = event.title
        event_datetime = event.event_datetime
        event_location = event.location

        rsvp = EventRSVP(
            id=uuid.uuid4(),
            event_id=event_id,
            name=name,
            email=email,
            message=message,
        )
        session.add(rsvp)
        session.commit()

    # =============== A. Email TO ADMIN ===============
    try:
        admin_body = (
            f"New RSVP for event '{event_title}'\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}\n"
        )
        send_email("yorkiebakery@gmail.com", f"New RSVP — {event_title}", admin_body)
    except Exception as e:
        print("⚠️ Failed to send admin RSVP email:", e)

    # =============== B. Confirmation TO USER ===============
    try:
        user_body = (
            f"Hi {name},\n\n"
            f"Thank you for RSVP’ing for:\n\n"
            f"📌 {event_title}\n"
            f"📅 {event_datetime}\n"
            f"📍 {event_location}\n\n"
            f"We’ll keep you updated about any announcements.\n\n"
            f"— Yorkie Bakery"
        )
        send_email(email, f"Your RSVP is Confirmed — {event_title}", user_body)
    except Exception as e:
        print("⚠️ Failed to send guest confirmation email:", e)

    return RedirectResponse("/events?success=1", status_code=303)


# ======================================================
# Admin: New Event Page
# ======================================================
@router.get("/new")
def admin_new_event(request: Request):
    require_admin(request)
    return templates.TemplateResponse("events_new.html", {"request": request})


# ======================================================
# Admin: Create Event
# ======================================================
@router.post("/new")
async def admin_create_event(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    date: str = Form(...),               # datetime-local input
    image: UploadFile = File(None),
):
    require_admin(request)

    # Convert ISO datetime string → Python datetime
    try:
        event_datetime = datetime.fromisoformat(date)
    except Exception:
        raise HTTPException(400, "Invalid date format. Must be datetime-local ISO format.")

    # ----------------------------
    # IMAGE → S3
    # ----------------------------
    image_url = None

    if image and image.filename:
        if image.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(
                status_code=400,
                detail="Image must be PNG or JPG."
            )

        image_url = upload_file_to_s3(
            image,
            folder="events",
            bucket="yorkiebakery-image"
        )

    # ----------------------------
    # SAVE EVENT IN DB
    # ----------------------------
    with Session(engine) as session:
        event = Event(
            id=uuid.uuid4(),
            title=title,
            description=description,
            location=location,
            event_datetime=event_datetime,
            image_url=image_url,
            is_active=True,
        )
        session.add(event)
        session.commit()

    return RedirectResponse("/events", status_code=303)

# ======================================================
# Admin: Send Notification to Event RSVPs
# ======================================================
@router.post("/notify/{event_id}")
def notify_event_attendees(
    event_id: UUID,
    request: Request,
    message: str = Form(...)
):
    require_admin(request)

    with Session(engine) as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(404, "Event not found")

        rsvps = session.exec(
            select(EventRSVP).where(EventRSVP.event_id == event_id)
        ).all()

    # Send email to each RSVP
    from app.core.send_email import send_event_notice

    sent = 0
    for r in rsvps:
        try:
            send_event_notice(r.email, event.title, message)
            sent += 1
        except Exception as e:
            print("Failed to send to", r.email, e)

    return RedirectResponse(
        f"/events?notified={sent}",
        status_code=303
    )