import os
import json
import sys

import boto3
from botocore.exceptions import NoCredentialsError, ClientError


def load_session_from_local_json():
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


def main() -> int:
    try:
        session = load_session_from_local_json() or boto3.session.Session()

        # 1) STS identity check (no bucket required)
        sts = session.client("sts")
        ident = sts.get_caller_identity()
        print(f"STS OK: Account={ident.get('Account')} Arn={ident.get('Arn')}")

        # 2) Optional: list buckets to confirm S3 access (will fail if not permitted)
        try:
            s3 = session.client("s3")
            resp = s3.list_buckets()
            names = [b["Name"] for b in resp.get("Buckets", [])]
            print(f"S3 list_buckets OK: {len(names)} bucket(s)")
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            print(f"S3 list_buckets not permitted or failed ({code}). Skipping.")

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






