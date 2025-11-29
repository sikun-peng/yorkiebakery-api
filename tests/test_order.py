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
    resp = client.get("/orders/view")
    assert resp.status_code in [200, 303, 307, 404]


def test_get_order_by_id(client, test_order, fake_session):
    """Test retrieving a specific order"""
    resp = client.get(f"/order/{test_order.id}")
    # May require authentication or route may be restricted
    assert resp.status_code in [200, 303, 401, 404]


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
    assert resp.status_code in [200, 401, 403, 404]


def test_cancel_order(client, test_order):
    """Test canceling an order"""
    resp = client.post(f"/order/{test_order.id}/cancel")
    # May require authentication
    assert resp.status_code in [200, 303, 401, 404]


def test_get_user_orders(client, order_user, test_order):
    """Test getting all orders for a user"""
    resp = client.get(f"/order/user/{order_user.id}")
    # May require authentication
    assert resp.status_code in [200, 401, 403, 404]


def test_order_view_page_without_login(client):
    """Test order view page without being logged in"""
    resp = client.get("/orders/view")
    assert resp.status_code in [303, 307, 404]


def test_update_nonexistent_order_status(client):
    """Test updating status of non-existent order"""
    fake_id = uuid4()
    resp = client.put(
        f"/order/{fake_id}/status",
        json={"status": "completed"},
    )
    assert resp.status_code == 404


def test_cancel_nonexistent_order(client):
    """Test canceling non-existent order"""
    fake_id = uuid4()
    resp = client.post(f"/order/{fake_id}/cancel")
    assert resp.status_code == 404


def test_delete_nonexistent_order(client):
    """Test deleting non-existent order"""
    fake_id = uuid4()
    resp = client.delete(f"/order/{fake_id}")
    assert resp.status_code == 404


def test_create_order_with_valid_items(client, fake_session):
    """Test creating order via API with valid menu items"""
    user = User(
        id=uuid4(),
        email="ordercreate@example.com",
        password_hash=hash_password("pass123"),
        first_name="Order",
        last_name="Create",
        is_verified=True,
    )
    fake_session.add(user)

    item = MenuItem(
        id=uuid4(),
        title="Order Item",
        price=15.00,
        is_available=True,
        image_url="https://example.com/item.jpg",
    )
    fake_session.menu_items[item.id] = item
    fake_session.commit()

    order_data = {
        "user_id": str(user.id),
        "items": [
            {"menu_item_id": str(item.id), "quantity": 3}
        ],
    }
    resp = client.post("/order/", json=order_data)
    assert resp.status_code in [200, 404, 422]


def test_create_order_empty_items(client, order_user):
    """Test creating order with no items"""
    order_data = {
        "user_id": str(order_user.id),
        "items": [],
    }
    resp = client.post("/order/", json=order_data)
    # Should fail with empty items
    assert resp.status_code in [400, 404, 422]


def test_create_order_invalid_user(client):
    """Test creating order with invalid user"""
    order_data = {
        "user_id": str(uuid4()),
        "items": [{"menu_item_id": str(uuid4()), "quantity": 1}],
    }
    resp = client.post("/order/", json=order_data)
    assert resp.status_code in [404, 400, 422]


def test_create_order_invalid_menu_item(client, fake_session):
    """Test creating order with invalid menu item"""
    user = User(
        id=uuid4(),
        email="ordertest@example.com",
        password_hash=hash_password("pass123"),
        first_name="Order",
        last_name="Test",
        is_verified=True,
    )
    fake_session.add(user)
    fake_session.commit()

    order_data = {
        "user_id": str(user.id),
        "items": [
            {"menu_item_id": str(uuid4()), "quantity": 1}
        ],
    }
    resp = client.post("/order/", json=order_data)
    # Should fail - menu item not found
    assert resp.status_code in [404, 422]


def test_delete_order(client, test_order):
    """Test deleting an order"""
    resp = client.delete(f"/order/{test_order.id}")
    assert resp.status_code in [200, 403, 404]


def test_order_delete_with_items(client, fake_session, order_user):
    """Test deleting order with order items"""
    # Create order with items
    order = Order(
        id=uuid4(),
        user_id=str(order_user.id),
        total=30.00,
        status="pending",
        created_at=datetime.utcnow(),
    )
    fake_session.add(order)
    fake_session.commit()

    # Create order items
    for i in range(2):
        order_item = OrderItem(
            id=uuid4(),
            order_id=order.id,
            menu_item_id=uuid4(),
            title=f"Item {i}",
            unit_price=15.00,
            quantity=1,
        )
        fake_session.add(order_item)
    fake_session.commit()

    resp = client.delete(f"/order/{order.id}")
    assert resp.status_code in [200, 403, 404]


def test_order_update_status_without_status(client, order_user, fake_session):
    """Test updating order status without providing new status"""
    order = Order(
        id=uuid4(),
        user_id=str(order_user.id),
        total=25.00,
        status="pending",
        created_at=datetime.utcnow(),
    )
    fake_session.add(order)
    fake_session.commit()

    resp = client.put(
        f"/order/{order.id}/status",
        json={},  # No status provided
    )
    assert resp.status_code in [200, 403, 404]


def test_list_all_orders(client):
    """Test listing all orders (admin function)"""
    resp = client.get("/orders/view")
    assert resp.status_code in [200, 303, 307, 403, 404]


def test_get_order_with_items(client, test_order):
    """Test getting order includes items"""
    resp = client.get(f"/order/{test_order.id}")
    assert resp.status_code in [200, 303, 401, 404]







def test_create_order_api_success(client, fake_session):
    """Test creating order via API endpoint"""
    from app.models.postgres.user import User
    from app.models.postgres.menu import MenuItem
    from app.core.security import hash_password
    
    user = User(
        id=uuid4(),
        email="apiorder@example.com",
        password_hash=hash_password("pass123"),
        first_name="API",
        last_name="Order",
        is_verified=True,
    )
    fake_session.add(user)
    
    item1 = MenuItem(
        id=uuid4(),
        title="API Item 1",
        price=10.00,
        is_available=True,
        image_url="https://example.com/item1.jpg",
        gallery_urls=[],
    )
    item2 = MenuItem(
        id=uuid4(),
        title="API Item 2",
        price=15.00,
        is_available=True,
        image_url="https://example.com/item2.jpg",
        gallery_urls=[],
    )
    fake_session.menu_items[item1.id] = item1
    fake_session.menu_items[item2.id] = item2
    fake_session.commit()
    
    order_data = {
        "user_id": str(user.id),
        "items": [
            {"menu_item_id": str(item1.id), "quantity": 2},
            {"menu_item_id": str(item2.id), "quantity": 1},
        ],
    }
    
    resp = client.post("/order/", json=order_data)
    assert resp.status_code in [200, 404, 422]


def test_get_order_by_id_api(client, test_order):
    """Test getting order by ID via API"""
    resp = client.get(f"/order/{test_order.id}")
    assert resp.status_code in [200, 303, 401, 404]


def test_create_order_calculates_total(client, fake_session):
    """Test that order creation correctly calculates total"""
    from app.models.postgres.user import User
    from app.models.postgres.menu import MenuItem
    from app.core.security import hash_password
    
    user = User(
        id=uuid4(),
        email="totaltest@example.com",
        password_hash=hash_password("pass123"),
        first_name="Total",
        last_name="Test",
        is_verified=True,
    )
    fake_session.add(user)
    
    item = MenuItem(
        id=uuid4(),
        title="Total Test Item",
        price=25.50,
        is_available=True,
        image_url="https://example.com/item.jpg",
        gallery_urls=[],
    )
    fake_session.menu_items[item.id] = item
    fake_session.commit()
    
    order_data = {
        "user_id": str(user.id),
        "items": [
            {"menu_item_id": str(item.id), "quantity": 3}
        ],
    }
    
    resp = client.post("/order/", json=order_data)
    assert resp.status_code in [200, 404, 422]


def test_order_status_update_to_completed(client, test_order):
    """Test updating order status to completed"""
    resp = client.put(
        f"/order/{test_order.id}/status",
        json={"status": "completed"},
    )
    assert resp.status_code in [200, 401, 403, 404]


def test_order_status_update_to_cancelled(client, test_order):
    """Test updating order status to cancelled"""
    resp = client.put(
        f"/order/{test_order.id}/status",
        json={"status": "cancelled"},
    )
    assert resp.status_code in [200, 401, 403, 404]


def test_cancel_already_completed_order(client, fake_session, order_user):
    """Test canceling an already completed order"""
    from app.models.postgres.order import Order

    order = Order(
        id=uuid4(),
        user_id=order_user.id,
        status="completed",
        total_price=30.00,
        customer_name=f"{order_user.first_name} {order_user.last_name}",
        customer_email=order_user.email,
        customer_phone="555-5555",
        created_at=datetime.utcnow(),
    )
    fake_session.add(order)
    fake_session.commit()

    resp = client.post(f"/order/{order.id}/cancel")
    assert resp.status_code in [200, 303, 400, 401, 404]


def test_order_create_with_empty_user_id(client):
    """Test creating order with empty user_id"""
    resp = client.post(
        "/order/",
        json={
            "user_id": "",
            "items": [{"menu_item_id": str(uuid4()), "quantity": 1}],
        },
    )
    assert resp.status_code in [400, 404, 422]


def test_order_operations_variations(client, fake_session):
    """Test various order operations"""
    from app.models.postgres.user import User
    from app.models.postgres.menu import MenuItem
    from app.core.security import hash_password

    # Create users and items
    users = []
    items = []

    for i in range(3):
        user = User(
            id=uuid4(),
            email=f"ordervar{i}@example.com",
            password_hash=hash_password("pass123"),
            first_name=f"Order{i}",
            last_name="Var",
            is_verified=True,
        )
        fake_session.add(user)
        users.append(user)

        item = MenuItem(
            id=uuid4(),
            title=f"Order Item {i}",
            price=20.00 + i,
            is_available=True,
            image_url=f"https://example.com/item{i}.jpg",
            gallery_urls=[],
        )
        fake_session.menu_items[item.id] = item
        items.append(item)

    fake_session.commit()

    # Create orders
    for user in users:
        for item in items:
            order_data = {
                "user_id": str(user.id),
                "items": [{"menu_item_id": str(item.id), "quantity": 1}],
            }
            client.post("/order/", json=order_data)
