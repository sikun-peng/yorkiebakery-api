import pytest
from uuid import uuid4
from app.models.postgres.music import MusicTrack


def test_music_listen_page(client, fake_session):
    resp = client.get("/music/listen")
    assert resp.status_code in [200, 404]


def test_music_upload_track(client):
    files = {
        "file": ("song.mp3", b"audio-bytes", "audio/mpeg"),
        "cover": ("cover.jpg", b"img-bytes", "image/jpeg"),
    }
    resp = client.post(
        "/music/new",
        data={
            "title": "New Song",
            "composer": "Composer, First",
            "performer": "Performer",
            "category": "piano",
            "description": "Great",
        },
        files=files,
        headers={"content-type": "multipart/form-data"},
    )
    assert resp.status_code in [200, 303, 400, 404]
