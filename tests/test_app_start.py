# tests/test_app_start.py

def test_app_start():
    from main import app
    assert app is not None