import boto3
from starlette.config import Config

config = Config(".env")

AWS_REGION = "us-west-2"
SES_SENDER = f"Yorkie Bakery <noreply@yorkiebakery.com>"

ses = boto3.client("ses", region_name=AWS_REGION)

def send_verification_email(email: str, token: str):
    verify_url = f"https://yorkiebakery.com/auth/verify/{token}"

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