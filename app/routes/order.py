from fastapi import APIRouter, HTTPException
from typing import List, Optional
from boto3.dynamodb.conditions import Key, Attr
from app.models.dynamo.order import Order

# --- FastAPI Router ---
router = APIRouter(prefix="/orders", tags=["orders"])

# --- Create ---
@router.post("/", response_model=Order)
def create_order(order: Order):
    try:
        orders_table.put_item(Item=order.dict())
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Get by ID ---
@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str):
    try:
        response = orders_table.get_item(Key={"id": order_id})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Order not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Get all ---
@router.get("/", response_model=List[Order])
def get_all_orders():
    try:
        response = orders_table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Get by user_id ---
@router.get("/user/{user_id}", response_model=List[Order])
def get_orders_by_user(user_id: str):
    try:
        response = orders_table.scan(
            FilterExpression=Attr("user_id").eq(user_id)
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Update ---
@router.put("/{order_id}", response_model=Order)
def update_order(order_id: str, updated_data: Order):
    try:
        response = orders_table.get_item(Key={"id": order_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Order not found")

        orders_table.put_item(Item=updated_data.dict())
        return updated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Delete ---
@router.delete("/{order_id}")
def delete_order(order_id: str):
    try:
        response = orders_table.get_item(Key={"id": order_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Order not found")

        orders_table.delete_item(Key={"id": order_id})
        return {"message": "Order deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))