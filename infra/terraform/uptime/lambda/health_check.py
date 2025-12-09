import json
import os
import urllib.request

HEALTH_URL = os.getenv("HEALTH_URL", "https://yorkiebakery.com/health")


def lambda_handler(event, context):
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=10) as resp:
            if resp.status == 200:
                return {"ok": True, "status": resp.status}
            raise Exception(f"Health check failed with status {resp.status}")
    except Exception as exc:
        # Raising ensures the Lambda Errors metric increments
        raise Exception(f"Health check failed: {exc}")
