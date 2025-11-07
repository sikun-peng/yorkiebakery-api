# app/core/ddb.py
import os
import time
from typing import Dict, Any, List

import boto3
from botocore.exceptions import ClientError

DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000")
DDB_REGION = os.getenv("AWS_REGION", "us-east-1")
DDB_TABLE = os.getenv("DDB_CART_TABLE", "carts")

_session = boto3.session.Session()
_dynamodb = _session.resource(
    "dynamodb",
    region_name=DDB_REGION,
    endpoint_url=DDB_ENDPOINT,
)
_table = None


def ensure_table() -> None:
    """Create the carts table if it doesn't exist (idempotent)."""
    global _table
    try:
        _table = _dynamodb.Table(DDB_TABLE)
        _table.load()
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    _dynamodb.create_table(
        TableName=DDB_TABLE,
        KeySchema=[{"AttributeName": "cart_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "cart_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    _table = _dynamodb.Table(DDB_TABLE)

    # wait for ACTIVE
    for _ in range(30):
        _table.load()
        if _table.table_status == "ACTIVE":
            break
        time.sleep(0.5)


def get_table():
    if _table is None:
        ensure_table()
    return _table


# -------- Cart helpers (simple structure) --------

def get_cart(cart_id: str) -> Dict[str, Any]:
    table = get_table()
    res = table.get_item(Key={"cart_id": cart_id})
    return res.get("Item") or {"cart_id": cart_id, "items": []}


def put_cart(cart: Dict[str, Any]) -> None:
    table = get_table()
    table.put_item(Item=cart)


def add_item(cart_id: str, menu_item_id: str, inc: int = 1) -> Dict[str, Any]:
    """Increment quantity for item; create cart if missing."""
    cart = get_cart(cart_id)
    items: List[Dict[str, Any]] = cart.get("items", [])
    found = False
    for it in items:
        if it["menu_item_id"] == menu_item_id:
            it["quantity"] = int(it.get("quantity", 0)) + inc
            if it["quantity"] <= 0:
                items = [x for x in items if x["menu_item_id"] != menu_item_id]
            found = True
            break
    if not found and inc > 0:
        items.append({"menu_item_id": menu_item_id, "quantity": inc})
    cart["items"] = items
    put_cart(cart)
    return cart


def remove_item(cart_id: str, menu_item_id: str, dec: int = 1) -> Dict[str, Any]:
    return add_item(cart_id, menu_item_id, inc=-dec)


def clear_cart(cart_id: str) -> None:
    table = get_table()
    table.delete_item(Key={"cart_id": cart_id})