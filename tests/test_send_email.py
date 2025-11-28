import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.email
def test_send_email(monkeypatch):
    """Test basic send_email function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_email

    send_email("test@example.com", "Test Subject", "Test Body")

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["test@example.com"]
    assert call_args[1]["Message"]["Subject"]["Data"] == "Test Subject"
    assert call_args[1]["Message"]["Body"]["Text"]["Data"] == "Test Body"


@pytest.mark.email
def test_send_event_notice(monkeypatch):
    """Test send_event_notice function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_event_notice

    send_event_notice("attendee@example.com", "Test Event", "Event update message")

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["attendee@example.com"]
    assert "Test Event" in call_args[1]["Message"]["Subject"]["Data"]


@pytest.mark.email
def test_send_verification_email(monkeypatch):
    """Test send_verification_email function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_verification_email

    verify_url = "http://example.com/verify?token=abc123"
    send_verification_email("newuser@example.com", verify_url)

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["newuser@example.com"]
    assert "Verify" in call_args[1]["Message"]["Subject"]["Data"]
    # Check both text and html versions
    assert verify_url in call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert verify_url in call_args[1]["Message"]["Body"]["Html"]["Data"]


@pytest.mark.email
def test_send_order_confirmation_email(monkeypatch):
    """Test send_order_confirmation_email function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_order_confirmation_email

    order_items = [
        {"title": "Croissant", "qty": 2, "price": 3.50},
        {"title": "Baguette", "qty": 1, "price": 4.00},
    ]
    total = 11.00

    send_order_confirmation_email("customer@example.com", order_items, total)

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["customer@example.com"]
    assert "Order Confirmation" in call_args[1]["Message"]["Subject"]["Data"]
    body = call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert "Croissant" in body
    assert "Baguette" in body
    assert "$11.00" in body


@pytest.mark.email
def test_send_owner_new_order_email(monkeypatch):
    """Test send_owner_new_order_email function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_owner_new_order_email

    order_items = [
        {"title": "Croissant", "qty": 2, "price": 3.50},
        {"title": "Baguette", "qty": 1, "price": 4.00},
    ]
    total = 11.00

    send_owner_new_order_email(order_items, total, "customer@example.com")

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["yorkiebakery@gmail.com"]
    assert "New Order" in call_args[1]["Message"]["Subject"]["Data"]
    body = call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert "customer@example.com" in body
    assert "Croissant" in body
    assert "$11.00" in body


@pytest.mark.email
def test_send_password_reset_email(monkeypatch):
    """Test send_password_reset_email function"""
    mock_ses = MagicMock()
    monkeypatch.setattr("app.core.send_email.ses", mock_ses)

    from app.core.send_email import send_password_reset_email

    reset_url = "http://example.com/reset?token=xyz789"
    send_password_reset_email("user@example.com", reset_url)

    mock_ses.send_email.assert_called_once()
    call_args = mock_ses.send_email.call_args
    assert call_args[1]["Destination"]["ToAddresses"] == ["user@example.com"]
    assert "Reset" in call_args[1]["Message"]["Subject"]["Data"]
    # Check both text and html versions
    assert reset_url in call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert reset_url in call_args[1]["Message"]["Body"]["Html"]["Data"]
    assert "1 hour" in call_args[1]["Message"]["Body"]["Text"]["Data"]
