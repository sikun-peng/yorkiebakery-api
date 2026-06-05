# tests/test_app_start.py

def test_app_start():
    from main import app
    assert app is not None


def test_request_body_limit_returns_413(client, monkeypatch):
    import main

    monkeypatch.setattr(main, "MAX_REQUEST_BODY_BYTES", 10)

    resp = client.post(
        "/menu/",
        data={"title": "Too Large", "price": "10.00"},
        headers={"content-length": "11"},
    )

    assert resp.status_code == 413
