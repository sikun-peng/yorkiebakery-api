import boto3
from starlette.config import Config

config = Config(".env")

AWS_REGION = "us-west-2"
SES_SENDER = f"Yorkie Bakery <noreply@beta.yorkiebakery.com>"

ses = boto3.client("ses", region_name=AWS_REGION)

def send_verification_email(email: str, token: str):
    verify_url = f"https://beta.yorkiebakery.com/auth/verify/{token}"

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Verify your Yorkie Bakery account 🐶🥐"},
            "Body": {
                "Text": {
                    "Data": f"Welcome! Click here to verify your account:\n{verify_url}\n\n- Yorkie Bakery"
                }
            }
        }
    )

def send_order_confirmation_email(email: str, order_items: list, total: float):
    item_list = "\n".join([f"{i['qty']} × {i['title']} (${i['price']})" for i in order_items])

    body = (
        "Thank you for your order from Yorkie Bakery!\n\n"
        "Your order:\n"
        f"{item_list}\n\n"
        f"Total: ${total:.2f}\n"
        "We will contact you when your order is ready.\n\n"
        "- Yorkie Bakery 🐶🥐"
    )

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Yorkie Bakery — Order Confirmation"},
            "Body": {"Text": {"Data": body}}
        }
    )

def send_owner_new_order_email(order_items: list, total: float, customer_email: str):
    lines = [
        f"{i['qty']} × {i['title']} — ${i['price']:.2f}"
        for i in order_items
    ]
    order_summary = "\n".join(lines)

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": ["yorkiebakery@gmail.com"]},
        Message={
            "Subject": {"Data": "📦 New Order Received — Yorkie Bakery"},
            "Body": {
                "Text": {
                    "Data": (
                        f"A new order has been placed.\n\n"
                        f"Customer: {customer_email}\n\n"
                        f"Order Summary:\n{order_summary}\n\n"
                        f"Total: ${total:.2f}\n\n"
                        f"Login to the admin panel for details."
                    )
                }
            },
        },
    )