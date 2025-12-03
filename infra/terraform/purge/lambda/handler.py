import os
import time
import logging
from urllib.parse import urlparse

import boto3
import pg8000.dbapi

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_db_url() -> str:
    param_name = os.environ.get("DB_PARAM_NAME")
    if not param_name:
        raise RuntimeError("DB_PARAM_NAME is required")
    ssm = boto3.client("ssm")
    resp = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return resp["Parameter"]["Value"]


def _get_grace_seconds() -> int:
    try:
        return int(os.environ.get("GRACE_SECONDS", "86400"))
    except Exception:
        return 86400


def handler(event, context):
    start = time.time()
    db_url = _get_db_url()
    grace_seconds = _get_grace_seconds()

    conn = None
    deleted = 0
    try:
        parsed = urlparse(db_url)
        if parsed.scheme not in ("postgresql", "postgres"):
            raise RuntimeError(f"Unsupported DB scheme: {parsed.scheme}")
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip("/") if parsed.path else None
        if not all([username, password, host, database]):
            raise RuntimeError("DATABASE_URL is missing username, password, host, or database name.")

        logger.info("Connecting to %s:%s", host, port)
        conn = pg8000.dbapi.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database,
            timeout=5,
        )

        sql = """
        DELETE FROM user_account
        WHERE is_verified = FALSE
          AND created_at < (NOW() - (%s * INTERVAL '1 second'));
        """
        conn.autocommit = False
        cur = conn.cursor()
        try:
            cur.execute(sql, (grace_seconds,))
            deleted = cur.rowcount or 0
            conn.commit()
        finally:
            cur.close()
        logger.info("Purged %s unverified users older than %s seconds", deleted, grace_seconds)
    except Exception as exc:
        logger.exception("Purge failed: %s", exc)
        raise
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    duration_ms = int((time.time() - start) * 1000)
    return {"deleted": deleted, "duration_ms": duration_ms, "grace_seconds": grace_seconds}
