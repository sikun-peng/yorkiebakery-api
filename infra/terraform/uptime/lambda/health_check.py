import os
import time
import urllib.request

HEALTH_URL = os.getenv("HEALTH_URL", "https://yorkiebakery.com/health")
ATTEMPTS = int(os.getenv("ATTEMPTS", "3"))
BACKOFF_SECONDS = float(os.getenv("BACKOFF_SECONDS", "1"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "YorkieBakery-Uptime/1.0 (+https://yorkiebakery.com)",
)


def _request_once():
    req = urllib.request.Request(
        HEALTH_URL,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if 200 <= resp.status < 300:
            return resp.status
        raise Exception(f"Health check failed with status {resp.status}")


def lambda_handler(event, context):
    last_exc = None
    for attempt in range(ATTEMPTS):
        try:
            status = _request_once()
            return {"ok": True, "status": status}
        except Exception as exc:
            last_exc = exc
            if attempt < ATTEMPTS - 1:
                # Linear backoff: 1s, 2s, 3s by default
                time.sleep(BACKOFF_SECONDS * (attempt + 1))

    # Raising ensures the Lambda Errors metric increments
    raise Exception(f"Health check failed after {ATTEMPTS} attempts: {last_exc}")
