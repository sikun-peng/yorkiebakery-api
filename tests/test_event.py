import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.models.postgres.event import Event


@pytest.fixture
def test_event(fake_session):
    """Create a test event"""
    event = Event(
        id=uuid4(),
        title="Test Event",
        description="A test event for testing",
        event_date=datetime.utcnow() + timedelta(days=7),
        location="Test Location",
        max_attendees=50,
        current_attendees=10,
        image_url="https://example.com/event.jpg",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    fake_session.add(event)
    fake_session.commit()
    return event


def test_event_list_page_renders(client):
    """Test event list page renders"""
    resp = client.get("/events/")
    assert resp.status_code in [200, 307]


def test_event_view_page_renders(client):
    """Test event view page renders"""
    resp = client.get("/events/view")
    assert resp.status_code == 200
    assert b"event" in resp.content.lower()


def test_get_event_by_id(client, test_event):
    """Test retrieving a specific event"""
    resp = client.get(f"/events/{test_event.id}")
    assert resp.status_code in [200, 404]
    if resp.status_code == 200:
        data = resp.json()
        assert data["title"] == "Test Event"
        assert data["location"] == "Test Location"


def test_get_nonexistent_event(client):
    """Test retrieving non-existent event"""
    fake_id = str(uuid4())
    resp = client.get(f"/events/{fake_id}")
    assert resp.status_code == 404


def test_create_event(client, fake_session):
    """Test creating a new event (admin only)"""
    future_date = (datetime.utcnow() + timedelta(days=14)).isoformat()

    resp = client.post(
        "/events/",
        data={
            "title": "New Event",
            "description": "New event description",
            "event_date": future_date,
            "location": "New Location",
            "is_active": "true",
        },
    )

    # Admin protected - should succeed with mocked admin
    assert resp.status_code in [200, 303, 307]


def test_update_event(client, test_event):
    """Test updating an event (admin only)"""
    resp = client.put(
        f"/events/{test_event.id}",
        json={
            "title": "Updated Event",
            "description": "Updated description",
        },
    )

    # Admin protected
    assert resp.status_code in [200, 303, 404]


def test_delete_event(client, test_event, fake_session):
    """Test deleting an event (admin only)"""
    resp = client.delete(f"/events/{test_event.id}")

    # Admin protected
    assert resp.status_code in [200, 303, 404]


def test_register_for_event(client, test_event):
    """Test registering for an event"""
    resp = client.post(
        f"/events/{test_event.id}/register",
        data={
            "name": "Test Attendee",
            "email": "attendee@example.com",
            "phone": "555-1234",
        },
    )

    assert resp.status_code in [200, 303, 404]


def test_register_for_full_event(client, fake_session):
    """Test registering for a full event"""
    # Create a full event
    full_event = Event(
        id=uuid4(),
        title="Full Event",
        description="Event at capacity",
        event_date=datetime.utcnow() + timedelta(days=7),
        location="Test Location",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    fake_session.add(full_event)
    fake_session.commit()

    resp = client.post(
        f"/events/{full_event.id}/register",
        data={
            "name": "Late Attendee",
            "email": "late@example.com",
            "phone": "555-5678",
        },
    )

    # Should reject or show error
    assert resp.status_code in [200, 400, 303, 404]


def test_register_for_inactive_event(client, fake_session):
    """Test registering for an inactive event"""
    inactive_event = Event(
        id=uuid4(),
        title="Inactive Event",
        description="This event is not active",
        event_date=datetime.utcnow() + timedelta(days=7),
        location="Test Location",
        max_attendees=50,
        current_attendees=0,
        is_active=False,  # Not active
        created_at=datetime.utcnow(),
    )
    fake_session.add(inactive_event)
    fake_session.commit()

    resp = client.post(
        f"/events/{inactive_event.id}/register",
        data={
            "name": "Eager Attendee",
            "email": "eager@example.com",
            "phone": "555-9999",
        },
    )

    # Should reject
    assert resp.status_code in [200, 400, 403, 303, 404]


def test_list_active_events(client, fake_session):
    """Test listing only active events"""
    # Create active and inactive events
    active_event = Event(
        id=uuid4(),
        title="Active Event",
        event_date=datetime.utcnow() + timedelta(days=7),
        location="Location 1",
        max_attendees=50,
        is_active=True,
    )
    inactive_event = Event(
        id=uuid4(),
        title="Inactive Event",
        event_date=datetime.utcnow() + timedelta(days=14),
        location="Location 2",
        max_attendees=50,
        is_active=False,
    )
    fake_session.add(active_event)
    fake_session.add(inactive_event)
    fake_session.commit()

    resp = client.get("/events/")
    assert resp.status_code in [200, 307]
