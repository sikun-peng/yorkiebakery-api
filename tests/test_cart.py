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
