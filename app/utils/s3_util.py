import boto3
import uuid
from fastapi import UploadFile

AWS_S3_REGION = "us-west-2"

s3_client = boto3.client("s3", region_name=AWS_S3_REGION)

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

    return f"https://{bucket}.s3.{AWS_S3_REGION}.amazonaws.com/{unique_filename}"