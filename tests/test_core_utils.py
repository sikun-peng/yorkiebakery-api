import pytest
from app.core.cart_utils import get_cart, get_cart_count
from app.core.logger import get_logger
from unittest.mock import Mock


def test_get_cart():
    """Test getting cart from request"""
    request = Mock()
    request.session = {"cart": {"item1": 2, "item2": 3}}

    cart = get_cart(request)
    assert cart is not None
    assert "item1" in cart
    assert cart["item1"] == 2


def test_get_cart_empty():
    """Test getting empty cart"""
    request = Mock()
    request.session = {}

    cart = get_cart(request)
    assert cart is not None
    assert isinstance(cart, dict)


def test_get_cart_count():
    """Test getting cart item count"""
    request = Mock()
    request.session = {"cart": {"item1": 2, "item2": 3, "item3": 1}}

    count = get_cart_count(request)
    assert count == 6  # 2 + 3 + 1


def test_get_cart_count_empty():
    """Test getting count for empty cart"""
    request = Mock()
    request.session = {}

    count = get_cart_count(request)
    assert count == 0


def test_get_logger():
    """Test logger initialization"""
    logger = get_logger("test_module")
    assert logger is not None
    assert logger.name == "test_module"


def test_get_logger_different_names():
    """Test that different names create different loggers"""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    assert logger1.name == "module1"
    assert logger2.name == "module2"
    assert logger1 is not logger2


def test_logger_can_log():
    """Test that logger can log messages"""
    logger = get_logger("test_logging")

    # Should not raise any exceptions
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    logger.debug("Test debug message")
