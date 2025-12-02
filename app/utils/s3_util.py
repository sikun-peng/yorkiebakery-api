import os
import uuid
import boto3
from fastapi import UploadFile

# Buckets / regions can be overridden in env so uploads work across stacks.
AWS_S3_REGION = os.getenv("AWS_REGION", "us-west-2")
S3_BUCKET_IMAGE = os.getenv("S3_BUCKET_IMAGE", "yorkiebakery-image")
S3_BUCKET_MUSIC = os.getenv("S3_BUCKET_MUSIC", "yorkiebakery-music")

# CDN base (optional). If unset, we fall back to the direct S3 URL.
# We use the same CDN host for all buckets by default.
IMAGE_CDN_BASE = os.getenv("IMAGE_CDN_BASE")  # e.g., https://d2pdj881wm30p5.cloudfront.net

s3_client = boto3.client("s3", region_name=AWS_S3_REGION)


def _build_public_url(bucket: str, key: str) -> str:
    """
    Return the public URL for the uploaded object.
    - Prefer IMAGE_CDN_BASE for any bucket if set.
    - Otherwise, fall back to the direct S3 URL.
    """
    if IMAGE_CDN_BASE:
        return f"{IMAGE_CDN_BASE}/{key}"
    return f"https://{bucket}.s3.{AWS_S3_REGION}.amazonaws.com/{key}"


def upload_file_to_s3(file: UploadFile, folder: str, bucket: str) -> str:
    if not bucket:
        raise RuntimeError("S3 bucket name must be provided")

    unique_filename = f"{folder}/{uuid.uuid4()}_{file.filename}"

    s3_client.upload_fileobj(
        file.file,
        Bucket=bucket,
        Key=unique_filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    return _build_public_url(bucket, unique_filename)
