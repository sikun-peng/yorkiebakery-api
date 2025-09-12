import boto3
from botocore.exceptions import ClientError
from app.schemas.order import Order
import os

def get_dynamodb_resource():
    """Return a DynamoDB resource, using local config if specified."""
    is_local = os.getenv("DYNAMO_LOCAL", "true").lower() == "true"

    if is_local:
        return boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:8001",  # local DynamoDB port
            region_name="us-west-2",
            aws_access_key_id="dummy",             # required even for local
            aws_secret_access_key="dummy"
        )
    else:
        return boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-west-2"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

def get_orders_table():
    """Return the orders table object"""
    dynamodb = get_dynamodb_resource()
    table_name = os.getenv("DYNAMO_ORDERS_TABLE", "YorkieOrders")
    return dynamodb.Table(table_name)

def save_order(order: Order) -> bool:
    """Save an order to DynamoDB"""
    try:
        table = get_orders_table()
        table.put_item(Item=order.dict())
        return True
    except ClientError as e:
        print(f"[DynamoDB] Failed to save order: {e}")
        return False