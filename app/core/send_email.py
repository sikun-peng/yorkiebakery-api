import boto3
from starlette.config import Config

config = Config(".env")

AWS_REGION = "us-west-2"
SES_SENDER = f"Yorkie Bakery <noreply@beta.yorkiebakery.com>"

ses = boto3.client("ses", region_name=AWS_REGION)

def send_email(to: str, subject: str, body: str):
    print(f"[SES] Sending email to: {to}")
    print(f"[SES] Subject: {subject}")
    print(f"[SES] Body preview: {body[:80]}...")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
    print("[SES] Email sent!")

def send_event_notice(email: str, event_title: str, message: str):
    subject = f"Update for {event_title} — Yorkie Bakery"
    body = (
        f"Hello,\n\n"
        f"There is an update regarding the event:\n"
        f"📌 {event_title}\n\n"
        f"{message}\n\n"
        f"— Yorkie Bakery"
    )

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        },
    )

def send_verification_email(email: str, verify_url: str):  # Changed parameter name
    print(f"DEBUG: Sending verification email to {email}")
    print(f"DEBUG: Verification URL: {verify_url}")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Verify your Yorkie Bakery account 🐶🥐"},
            "Body": {
                "Text": {
                    "Data": f"Welcome! Click here to verify your account:\n{verify_url}\n\n- Yorkie Bakery"
                },
                "Html": {
                    "Data": f"""
                    <html>
                    <body>
                        <h2>Verify your Yorkie Bakery account 🐶🥐</h2>
                        <p>Welcome! Click the link below to verify your account:</p>
                        <p><a href="{verify_url}" style="background: #ffb36b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Account</a></p>
                        <p>Or copy and paste this URL in your browser:</p>
                        <p><code>{verify_url}</code></p>
                        <hr>
                        <p><small>If you didn't create this account, please ignore this email.</small></p>
                    </body>
                    </html>
                    """
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
        "- Oscar Peng 🐶🥐"
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


def send_password_reset_email(email: str, reset_url: str):
    print(f"DEBUG: Sending password reset email to {email}")
    print(f"DEBUG: Reset URL: {reset_url}")

    subject = "Reset Your Yorkie Bakery Password 🐶🥐"

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Text": {
                    "Data": f"Click here to reset your password:\n{reset_url}\n\nThis link expires in 1 hour."
                },
                "Html": {
                    "Data": f"""
                    <html>
                    <body>
                        <h2>Reset Your Password</h2>
                        <p>Click the link below to reset your Yorkie Bakery password:</p>
                        <p><a href="{reset_url}" style="background: #ffb36b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a></p>
                        <p>Or copy and paste this URL in your browser:</p>
                        <p><code>{reset_url}</code></p>
                        <hr>
                        <p><small>If you didn't request a password reset, please ignore this email.</small></p>
                    </body>
                    </html>
                    """
                }
            }
        }
    )
    print(f"DEBUG: Password reset email sent successfully to {email}")