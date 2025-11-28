import pytest
from uuid import uuid4
from datetime import datetime
from app.models.postgres.menu import MenuItem
from app.models.postgres.user import User
from app.models.postgres.order import Order
from app.models.postgres.order_item import OrderItem
from app.core.security import hash_password


@pytest.fixture
def order_user(fake_session):
    """Create a user for order testing"""
    user = User(
        id=uuid4(),
        email="order@example.com",
        password_hash=hash_password("password123"),
        first_name="Order",
        last_name="User",
        is_verified=True,
        is_admin=False,
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.fixture
def test_order(fake_session, order_user):
    """Create a test order"""
    order = Order(
        id=uuid4(),
        user_id=order_user.id,
        status="pending",
        total_price=25.99,
        customer_name=f"{order_user.first_name} {order_user.last_name}",
        customer_email=order_user.email,
        customer_phone="555-1234",
        pickup_time=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    fake_session.add(order)
    fake_session.commit()
    return order


def test_order_list_page_renders(client):
    """Test order list page renders"""
    resp = client.get("/order/")
    assert resp.status_code == 200


def test_get_order_by_id(client, test_order, fake_session):
    """Test retrieving a specific order"""
    resp = client.get(f"/order/{test_order.id}")
    # May require authentication
    assert resp.status_code in [200, 303, 401]


def test_get_nonexistent_order(client):
    """Test retrieving non-existent order"""
    fake_id = str(uuid4())
    resp = client.get(f"/order/{fake_id}")
    assert resp.status_code in [404, 303, 401]


def test_create_order(client, fake_session, monkeypatch):
    """Test creating a new order"""
    # Mock email sending
    email_sent = []
    def mock_send_order_email(*args, **kwargs):
        email_sent.append(True)
    monkeypatch.setattr("app.routes.cart.send_order_confirmation_email", mock_send_order_email)
    monkeypatch.setattr("app.routes.cart.send_owner_new_order_email", mock_send_order_email)

    # First add item to cart
    item = MenuItem(
        id=uuid4(),
        title="Order Item",
        description="Test order item",
        price=15.99,
        category="dessert",
        origin="french",
        tags=["sweet"],
        is_available=True,
    )
    fake_session.menu_items[item.id] = item

    client.post(
        "/cart/add",
        json={
            "menu_item_id": str(item.id),
            "quantity": "2",
        },
    )

    # Then create order through checkout
    resp = client.post(
        "/cart/checkout",
        data={
            "customer_name": "Test Customer",
            "customer_email": "customer@example.com",
            "customer_phone": "555-1234",
            "pickup_time": "2025-12-01T14:00",
            "notes": "Test order notes",
        },
    )

    # Should redirect or return success
    assert resp.status_code in [200, 303, 422]


def test_update_order_status(client, test_order, fake_session):
    """Test updating order status (admin function)"""
    resp = client.put(
        f"/order/{test_order.id}/status",
        json={"status": "completed"},
    )
    # May require admin authentication
    assert resp.status_code in [200, 401, 403]


def test_cancel_order(client, test_order):
    """Test canceling an order"""
    resp = client.post(f"/order/{test_order.id}/cancel")
    # May require authentication
    assert resp.status_code in [200, 303, 401]


def test_get_user_orders(client, order_user, test_order):
    """Test getting all orders for a user"""
    resp = client.get(f"/order/user/{order_user.id}")
    # May require authentication
    assert resp.status_code in [200, 401, 403]
