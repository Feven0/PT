import os
import sys
import json
import time
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Use the app's secret helper as requested
def get_bucket_from_secrets_manager(session) -> str:
    try:
        sm = session.client('secretsmanager')
        resp = sm.get_secret_value(SecretId='tenx/env/vars')
        if 'SecretString' in resp:
            data = json.loads(resp['SecretString'])
        else:
            import base64
            data = json.loads(base64.b64decode(resp['SecretBinary']).decode('utf-8'))
        return (data or {}).get('S3_BUCKET', '').strip()
    except Exception:
        return ''


def load_session_from_local_json():
    """
    If .env/aws_config.json exists, create and return a boto3.Session using it.
    Otherwise return None to fall back to default credential chain.
    """
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


def get_bucket_name(session):
    # Try Secrets Manager first, then fallback to app config default
    bucket = get_bucket_from_secrets_manager(session)
    if not bucket:
        # Use the same default as api.config.s3.zlm_bucket
        bucket = 'tenx-tinder4job'
    return bucket


def main() -> int:
    session = load_session_from_local_json() or boto3.session.Session()
    bucket = get_bucket_name(session)
    if not bucket:
        print("ERROR: No S3 bucket configured. Set S3_TEST_BUCKET or S3_BUCKET, or api.config.s3.zlm_bucket.")
        return 2

    s3 = session.client("s3")

    key = f"connectivity_test/{int(time.time())}_probe.txt"
    payload = f"s3 connectivity probe at {datetime.utcnow().isoformat()}Z\n"

    try:
        print(f"Uploading s3://{bucket}/{key} ...")
        s3.put_object(Bucket=bucket, Key=key, Body=payload.encode("utf-8"))

        print("Verifying object exists ...")
        s3.head_object(Bucket=bucket, Key=key)

        print("Cleaning up test object ...")
        s3.delete_object(Bucket=bucket, Key=key)

        print("SUCCESS: S3 connectivity verified.")
        return 0
    except NoCredentialsError:
        print("ERROR: No AWS credentials found. Configure environment or .env/aws_config.json.")
        return 3
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        print(f"ERROR: AWS ClientError {code}: {e}")
        return 4
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


