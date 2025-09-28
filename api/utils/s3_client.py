import os
import json
import time
from datetime import datetime
from typing import Optional, Tuple

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, NoCredentialsError


def _load_session_from_local_json() -> Optional[boto3.session.Session]:
    cfg_path = os.path.join(os.getcwd(), ".env", "aws_config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            data = json.load(f)
        return boto3.session.Session(
            aws_access_key_id=data.get("aws_access_key_id"),
            aws_secret_access_key=data.get("aws_secret_access_key"),
            region_name=data.get("region_name", os.getenv("AWS_DEFAULT_REGION", "us-east-1")),
        )
    return None


def get_s3_client() -> BaseClient:
    """
    Return a boto3 S3 client using .env/aws_config.json if present,
    otherwise the default AWS credential chain.
    """
    session = _load_session_from_local_json() or boto3.session.Session()
    return session.client("s3")


def list_buckets() -> list:
    """
    List available S3 buckets for the current credentials.

    Returns:
        list[str]: Bucket names.
    """
    s3 = get_s3_client()
    resp = s3.list_buckets()
    return [b["Name"] for b in resp.get("Buckets", [])]


def upload_file_and_get_url(
    bucket_name: str,
    local_file_path: str,
    key: Optional[str] = None,
    expires_in_seconds: int = 900,
) -> Tuple[str, str]:
    """
    Upload a local file to the specified S3 bucket and return a presigned GET URL.

    Args:
        bucket_name: Destination S3 bucket name.
        local_file_path: Path to the local file to upload.
        key: Object key to store as. If None, a timestamped key is generated.
        expires_in_seconds: Presigned URL expiry in seconds.

    Returns:
        (bucket, key): Tuple of bucket and object key. The presigned URL is returned separately.

    Raises:
        FileNotFoundError: If local_file_path does not exist.
        NoCredentialsError, ClientError: If AWS credentials or permissions are invalid.
    """
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(local_file_path)

    s3 = get_s3_client()

    if key is None:
        ts = int(time.time())
        base = os.path.basename(local_file_path)
        key = f"uploads/{ts}_{base}"

    with open(local_file_path, "rb") as fh:
        s3.put_object(Bucket=bucket_name, Key=key, Body=fh.read())

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=expires_in_seconds,
    )

    return url, key


def upload_bytes_and_get_url(
    bucket_name: str,
    data: bytes,
    key: Optional[str] = None,
    expires_in_seconds: int = 31536000,  # 1 year in seconds
) -> Tuple[str, str]:
    """
    Upload in-memory bytes to S3 and return a long-term presigned URL.
    """
    s3 = get_s3_client()

    if key is None:
        ts = int(time.time())
        key = f"uploads/{ts}_blob.bin"

    s3.put_object(Bucket=bucket_name, Key=key, Body=data)

    # Return long-term presigned URL (1 year expiration)
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=expires_in_seconds,
    )

    return url, key


