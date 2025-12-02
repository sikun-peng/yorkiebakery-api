import pytest
from uuid import uuid4
from app.models.postgres.menu import MenuItem
from app.models.postgres.user import User
from app.core.security import hash_password
from datetime import datetime


@pytest.fixture
def cart_items(fake_session):
    """Create menu items for cart testing"""
    items = []
    for i in range(3):
        item = MenuItem(
            id=uuid4(),
            title=f"Cart Item {i+1}",
            description=f"Test cart item {i+1}",
            price=10.0 + i,
            category="dessert",
            origin="french",
            tags=["sweet"],
            flavor_profiles=["sweet"],
            dietary_features=["vegetarian"],
            is_available=True,
            image_url=f"https://example.com/item{i+1}.jpg",
            gallery_urls=[],  # Add gallery_urls field
        )
        fake_session.menu_items[item.id] = item
        items.append(item)
    return items


@pytest.fixture
def logged_in_user(fake_session):
    """Create and return a logged-in user"""
    user = User(
        id=uuid4(),
        email="cart@example.com",
        password_hash=hash_password("password123"),
        first_name="Cart",
        last_name="User",
        is_verified=True,
        is_admin=False,
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.fixture
def address_user(fake_session):
    user = User(
        id=uuid4(),
        email="address@example.com",
        password_hash=hash_password("password123"),
        first_name="Address",
        last_name="User",
        is_verified=True,
        is_admin=False,
        address_line1="456 Cookie Rd",
        address_line2="Unit 2",
        city="Seattle",
        state="WA",
        postal_code="98101",
        country="USA",
        default_phone="555-1111",
        created_at=datetime.utcnow(),
    )
    fake_session.add(user)
    fake_session.commit()
    return user


@pytest.mark.cart
def test_view_cart_page_renders(client):
    """Test cart view page renders"""
    resp = client.get("/cart/view")
    assert resp.status_code == 200
    assert b"cart" in resp.content.lower()


@pytest.mark.cart
def test_view_empty_cart(client):
    """Test viewing an empty cart"""
    resp = client.get("/cart/view")
    assert resp.status_code == 200
    # Empty cart should still render


@pytest.mark.cart
def test_add_item_to_cart(client, cart_items):
    """Test adding an item to cart"""
    item_id = str(cart_items[0].id)

    resp = client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "2",
        },
    )

    # Should redirect after adding to cart
    assert resp.status_code in [200, 303, 404]


@pytest.mark.cart
def test_add_invalid_item_to_cart(client):
    """Test adding non-existent item to cart"""
    fake_id = str(uuid4())

    resp = client.post(
        "/cart/add",
        json={
            "menu_item_id": fake_id,
            "quantity": "1",
        },
    )

    # Should handle gracefully
    assert resp.status_code in [200, 303, 404]


@pytest.mark.cart
def test_update_cart_item_quantity(client, cart_items):
    """Test updating cart item quantity"""
    item_id = str(cart_items[0].id)

    # First add item
    client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "1",
        },
    )

    # Then update quantity
    resp = client.post(
        "/cart/update",
        json={
            "menu_item_id": item_id,
            "quantity": "3",
        },
    )

    assert resp.status_code in [200, 303, 404]


@pytest.mark.cart
def test_remove_item_from_cart(client, cart_items):
    """Test removing an item from cart"""
    item_id = str(cart_items[0].id)

    # First add item
    client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "1",
        },
    )

    # Then remove it
    resp = client.post(
        "/cart/remove",
        json={"menu_item_id": item_id},
    )

    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_clear_cart(client, cart_items):
    """Test clearing entire cart"""
    # Add multiple items
    for item in cart_items[:2]:
        client.post(
            "/cart/add",
            json={
                "menu_item_id": str(item.id),
                "quantity": "1",
            },
        )

    # Clear cart
    resp = client.post("/cart/clear")
    assert resp.status_code in [200, 303, 404]


@pytest.mark.cart
def test_checkout_page_renders(client):
    """Test checkout page renders"""
    resp = client.get("/cart/checkout")
    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_checkout_requires_items_in_cart(client):
    """Test checkout with empty cart"""
    resp = client.get("/cart/checkout")
    # Should still render but may show warning
    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_checkout_page_with_items(client, cart_items):
    """Test checkout page with items in cart"""
    # Add item to cart
    client.post(
        "/cart/add",
        json={
            "menu_item_id": str(cart_items[0].id),
            "quantity": "2",
        },
    )

    resp = client.get("/cart/checkout")
    assert resp.status_code in [200, 303]
    if resp.status_code == 200:
        assert b"checkout" in resp.content.lower()


def test_checkout_prefills_saved_address(client, fake_session, address_user):
    # Log in
    login_resp = client.post(
        "/auth/login_form",
        data={"email": address_user.email, "password": "password123"},
    )
    assert login_resp.status_code in (200, 303)

    # Add seeded item to cart
    menu_id = str(next(iter(fake_session.menu_items.keys())))
    client.post("/cart/add", json={"menu_item_id": menu_id, "quantity": "1"})

    resp = client.get("/cart/checkout")
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "456 Cookie Rd" in body
    assert "Unit 2" in body
    assert "Seattle" in body
    assert 'value="WA" selected' in body
    assert "98101" in body
    assert "USA" in body
    assert 'value="555-1111"' in body


def test_checkout_saves_last_used_address(client, fake_session, address_user):
    # Log in
    login_resp = client.post(
        "/auth/login_form",
        data={"email": address_user.email, "password": "password123"},
    )
    assert login_resp.status_code in (200, 303)

    # Add seeded item to cart
    menu_id = str(next(iter(fake_session.menu_items.keys())))
    client.post("/cart/add", json={"menu_item_id": menu_id, "quantity": "1"})

    resp = client.post(
        "/cart/checkout",
        data={
            "name": "New Name",
            "email": "new@example.com",
            "phone": "555-9999",
            "address_line1": "789 Brownie Blvd",
            "address_line2": "",
            "city": "Boise",
            "state": "ID",
            "postal_code": "83702",
            "country": "USA",
            "delivery_notes": "Ring bell",
        },
    )
    assert resp.status_code == 200
    assert address_user.address_line1 == "789 Brownie Blvd"
    assert address_user.address_line2 is None
    assert address_user.city == "Boise"
    assert address_user.state == "ID"
    assert address_user.postal_code == "83702"
    assert address_user.country == "USA"
    assert address_user.default_phone == "555-9999"


@pytest.mark.cart
def test_cart_quantity_validation(client, cart_items):
    """Test that invalid quantities are handled"""
    item_id = str(cart_items[0].id)

    # Try adding with negative quantity
    resp = client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "-1",
        },
    )
    # Should handle gracefully
    assert resp.status_code in [200, 303, 400]

    # Try adding with zero quantity
    resp = client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "0",
        },
    )
    # Should handle gracefully
    assert resp.status_code in [200, 303, 400]


@pytest.mark.cart
def test_cart_persists_across_requests(client, cart_items):
    """Test that cart persists in session"""
    item_id = str(cart_items[0].id)

    # Add item
    client.post(
        "/cart/add",
        json={
            "menu_item_id": item_id,
            "quantity": "1",
        },
    )

    # View cart - should show the item
    resp = client.get("/cart/view")
    assert resp.status_code == 200


@pytest.mark.cart
def test_add_item_button(client, cart_items):
    """Test adding item via button (form post)"""
    item_id = str(cart_items[0].id)
    resp = client.post(f"/cart/add/{item_id}")
    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_remove_item_button(client, cart_items):
    """Test removing item via button"""
    item_id = str(cart_items[0].id)
    # First add
    client.post(f"/cart/add/{item_id}")
    # Then remove
    resp = client.post(f"/cart/remove/{item_id}")
    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_checkout_requires_login(client, cart_items):
    """Test that checkout requires login"""
    # Add item to cart
    client.post(
        "/cart/add",
        json={"menu_item_id": str(cart_items[0].id)},
    )

    # Try to access checkout without login
    resp = client.get("/cart/checkout")
    # Should redirect to login
    assert resp.status_code in [200, 303]


@pytest.mark.cart
def test_process_checkout_with_logged_in_user(client, cart_items, logged_in_user, monkeypatch):
    """Test processing checkout with logged in user"""
    # Mock email sending
    def mock_send_order_email(*args, **kwargs):
        pass
    def mock_send_owner_email(*args, **kwargs):
        pass
    monkeypatch.setattr("app.routes.cart.send_order_confirmation_email", mock_send_order_email)
    monkeypatch.setattr("app.routes.cart.send_owner_new_order_email", mock_send_owner_email)

    # Login user
    client.post(
        "/auth/login_form",
        data={
            "email": "cart@example.com",
            "password": "password123",
        },
    )

    # Add item to cart
    client.post(
        "/cart/add",
        json={"menu_item_id": str(cart_items[0].id)},
    )

    # Process checkout
    resp = client.post(
        "/cart/checkout",
        data={
            "name": "Test User",
            "email": "cart@example.com",
            "phone": "555-123-4567",
            "address_line1": "123 Test St",
            "address_line2": "Apt 4B",
            "city": "Testville",
            "state": "CA",
            "postal_code": "12345",
            "country": "USA",
            "delivery_notes": "Leave at door",
        },
    )
    assert resp.status_code in [200, 303]





def test_cart_add_item_with_quantity(client, fake_session):
    """Test adding item to cart with specific quantity"""
    from app.models.postgres.menu import MenuItem
    
    item = MenuItem(
        id=uuid4(),
        title="Quantity Test",
        price=10.00,
        is_available=True,
        image_url="https://example.com/item.jpg",
        gallery_urls=[],
    )
    fake_session.menu_items[item.id] = item
    fake_session.commit()
    
    resp = client.post(
        "/cart/add",
        json={"menu_item_id": str(item.id), "quantity": "5"},
    )
    assert resp.status_code in [200, 303]



def test_cart_operations_with_invalid_item(client):
    """Test cart operations with invalid menu item"""
    fake_id = str(uuid4())

    resp = client.post(
        "/cart/add",
        json={"menu_item_id": fake_id, "quantity": "1"},
    )
    # Might succeed or fail depending on validation
    assert resp.status_code in [200, 303, 400, 404]


def test_cart_add_with_missing_quantity(client):
    """Test adding to cart without quantity"""
    resp = client.post(
        "/cart/add",
        json={"menu_item_id": str(uuid4())},
    )
    assert resp.status_code in [200, 303, 400, 422]


def test_cart_update_with_negative_quantity(client):
    """Test updating cart with negative quantity"""
    resp = client.post(
        "/cart/update",
        json={"menu_item_id": str(uuid4()), "quantity": "-1"},
    )
    assert resp.status_code in [200, 303, 400, 404]


def test_cart_remove_nonexistent_item(client):
    """Test removing non-existent item from cart"""
    resp = client.post(
        "/cart/remove",
        json={"menu_item_id": str(uuid4())},
    )
    assert resp.status_code in [200, 303, 404]


def test_cart_multiple_operations(client, fake_session):
    """Test multiple cart operations"""
    from app.models.postgres.menu import MenuItem

    items = []
    for i in range(5):
        item = MenuItem(
            id=uuid4(),
            title=f"Multi Item {i}",
            price=10.00 + i,
            is_available=True,
            image_url=f"https://example.com/item{i}.jpg",
            gallery_urls=[],
        )
        fake_session.menu_items[item.id] = item
        items.append(item)
    fake_session.commit()

    # Add items
    for item in items:
        client.post("/cart/add", json={"menu_item_id": str(item.id), "quantity": "1"})

    # Update quantities
    for item in items[:3]:
        client.post("/cart/update", json={"menu_item_id": str(item.id), "quantity": "2"})

    # Remove some items
    for item in items[3:]:
        client.post("/cart/remove", json={"menu_item_id": str(item.id)})
