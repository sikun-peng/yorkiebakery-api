import boto3
from typing import Optional, Union
from starlette.config import Config
from app.core.logger import get_logger

logger = get_logger(__name__)

config = Config(".env")

AWS_REGION = "us-west-2"
SES_SENDER = f"Yorkie Bakery <noreply@yorkiebakery.com>"
SES_CONFIG_SET = "my-first-configuration-set"

ses = boto3.client("ses", region_name=AWS_REGION)


def _format_price(amount: Optional[Union[float, int]]) -> str:
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"

def send_email(to: str, subject: str, body: str):
    logger.info(f"Sending email to: {to}")
    logger.debug(f"Subject: {subject}")
    logger.debug(f"Body preview: {body[:80]}...")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        },
        ConfigurationSetName=SES_CONFIG_SET
    )
    logger.info(f"Email sent successfully to {to}")

def send_event_notice(email: str, event_title: str, message: str):
    subject = f"⚠️ Yorkie Bakery - Event Update for {event_title}"
    body = (
        f"Hello,\n\n"
        f"There is an update regarding the event:\n"
        f"📌 {event_title}\n\n"
        f"{message}\n\n"
        f"— Yorkie Bakery Customer Service"
    )

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        },
        ConfigurationSetName=SES_CONFIG_SET
    )

def send_verification_email(email: str, verify_url: str):  # Changed parameter name
    logger.info(f"Sending verification email to {email}")
    logger.info(f"Verification URL: {verify_url}")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "👤 Yorkie Bakery - Please Verify Your Account"},
            "Body": {
                "Text": {
                    "Data": f"Welcome! Click here to verify your account:\n{verify_url}\n\n- Yorkie Bakery"
                },
                "Html": {
                    "Data": f"""
                    <html>
                    <body>
                        <h2>Verify your Yorkie Bakery account 🐶</h2>
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
        },
        ConfigurationSetName=SES_CONFIG_SET
    )

def send_password_changed_email(email: str, first_name: Optional[str] = None):
    subject = "🔐 Yorkie Bakery - Your Password Has Been Updated"
    greeting = f"Hi {first_name}," if first_name else "Hi there,"
    body = (
        f"{greeting}\n\n"
        "This is a confirmation that the password for your Yorkie Bakery account has been successfully updated.\n"
        "If you did not request this change, please reset your password immediately or reach out to our support team at any time.\n\n"
        "Best regards,\n"
        "Yorkie Bakery Security Team 🐶"
    )

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        },
        ConfigurationSetName=SES_CONFIG_SET
    )

def send_order_confirmation_email(
    email: str,
    order_items: list,
    total: float,
    customer_name: Optional[str] = None,
    delivery_address: Optional[str] = None,
    phone: Optional[str] = None,
    delivery_notes: Optional[str] = None,
    order_id: Optional[str] = None,
    order_url: Optional[str] = None,
    discount_percent: Optional[float] = None,
    original_total: Optional[float] = None,
):
    order_ref = (order_id or "").split("-")[0] if order_id else None

    def format_line(item):
        qty = item.get("qty", 1)
        title = item.get("title", "Item")
        price = item.get("price", 0)
        subtotal = price * qty
        return f"- {qty} × {title} @ {_format_price(price)} = {_format_price(subtotal)}"

    item_list = "\n".join([format_line(i) for i in order_items])

    contact_lines = []
    if customer_name:
        contact_lines.append(f"Name: {customer_name}")
    if delivery_address:
        contact_lines.append(f"Address: {delivery_address}")
    if phone:
        contact_lines.append(f"Phone: {phone}")
    if delivery_notes:
        contact_lines.append(f"Notes: {delivery_notes}")

    contact_block = "\n".join(contact_lines)
    contact_section = f"\n\nContact Info:\n{contact_block}" if contact_block else ""

    totals_lines = []
    if original_total is not None:
        totals_lines.append(f"Subtotal: {_format_price(original_total)}")
    if discount_percent is not None:
        totals_lines.append(f"Discount: {discount_percent:.0f}% off")
    totals_lines.append(f"Total: {_format_price(total)}")
    totals_block = "\n".join(totals_lines)

    header = f"Hi{f' {customer_name}' if customer_name else ''}, thanks for your order!"
    if order_ref:
        header = f"{header} Order #{order_ref}"

    next_steps = "We’ll email you when it’s on the way."
    cta_line = f"View your order: {order_url}" if order_url else ""
    promo_line = ""
    if discount_percent is not None and discount_percent >= 100:
        promo_line = "100% off promo applied."

    body = (
        f"{header}\n\n"
        "Your order:\n"
        f"{item_list}\n\n"
        f"{totals_block}\n"
        f"{promo_line}\n\n"
        f"{next_steps}\n"
        f"{cta_line}\n"
        f"{contact_section}\n\n"
        "Best Regards,\n"
        "Oscar Peng 🎉🎁"
    )

    logger.info(f"Sending order confirmation to {email} for order {order_ref or order_id or 'unknown'}")
    logger.debug(f"Order confirmation subject suffix: {order_ref}")
    logger.debug(f"Order confirmation body preview: {body[:160]}...")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": f"📦 Yorkie Bakery — Order Confirmation{f' #{order_ref}' if order_ref else ''}"},
            "Body": {"Text": {"Data": body}}
        },
        ConfigurationSetName=SES_CONFIG_SET
    )

def send_owner_new_order_email(
    order_items: list,
    total: float,
    customer_email: str,
    customer_name: Optional[str] = None,
    delivery_address: Optional[str] = None,
    phone: Optional[str] = None,
    delivery_notes: Optional[str] = None,
    order_id: Optional[str] = None,
    order_url: Optional[str] = None,
    discount_percent: Optional[float] = None,
    original_total: Optional[float] = None,
):
    order_ref = (order_id or "").split("-")[0] if order_id else None

    def format_line(item):
        qty = item.get("qty", 1)
        title = item.get("title", "Item")
        price = item.get("price", 0)
        subtotal = price * qty
        return f"- {qty} × {title} @ {_format_price(price)} = {_format_price(subtotal)}"

    lines = [
        format_line(i)
        for i in order_items
    ]
    order_summary = "\n".join(lines)

    contact_lines = [
        f"Customer Email: {customer_email}",
    ]
    if customer_name:
        contact_lines.append(f"Name: {customer_name}")
    if delivery_address:
        contact_lines.append(f"Address: {delivery_address}")
    if phone:
        contact_lines.append(f"Phone: {phone}")
    if delivery_notes:
        contact_lines.append(f"Notes: {delivery_notes}")
    contact_block = "\n".join(contact_lines)

    totals_lines = []
    if original_total is not None:
        totals_lines.append(f"Subtotal: {_format_price(original_total)}")
    if discount_percent is not None:
        totals_lines.append(f"Discount: {discount_percent:.0f}% off")
    totals_lines.append(f"Total: {_format_price(total)}")
    totals_block = "\n".join(totals_lines)

    cta_line = f"Order page: {order_url}" if order_url else ""

    logger.info(f"Sending owner new order email for order {order_ref or order_id or 'unknown'} to yorkiebakery@gmail.com")
    logger.debug(f"Owner email subject suffix: {order_ref}")
    logger.debug(f"Owner email body preview: {order_summary[:160]}...")

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": ["yorkiebakery@gmail.com"]},
        Message={
            "Subject": {"Data": f"📦 Yorkie Bakery - New Order Received{f' #{order_ref}' if order_ref else ''}"},
            "Body": {
                "Text": {
                    "Data": (
                        f"A new order has been placed{f' (#{order_ref})' if order_ref else ''}.\n\n"
                        f"{contact_block}\n\n"
                        f"Order Summary:\n{order_summary}\n\n"
                        f"{totals_block}\n\n"
                        f"{cta_line}\n"
                        f"Login to the admin panel for details."
                    )
                }
            },
        },
        ConfigurationSetName=SES_CONFIG_SET
    )


def send_password_reset_email(email: str, reset_url: str):
    logger.info(f"Sending password reset email to {email}")
    logger.info(f"Reset URL: {reset_url}")

    subject = "🔐 Yorkie Bakery - Reset Your Password"

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
        },
        ConfigurationSetName=SES_CONFIG_SET
    )
    logger.info(f"Password reset email sent successfully to {email}")
