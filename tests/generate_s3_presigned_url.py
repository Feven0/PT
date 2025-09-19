import os
import json
import time
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


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


def choose_bucket(session) -> str:
    bucket = get_bucket_from_secrets_manager(session)
    if not bucket:
        bucket = 'tenx-tinder4job'
    return bucket


def main() -> int:
    try:
        session = load_session_from_local_json() or boto3.session.Session()
        s3 = session.client('s3')

        bucket = choose_bucket(session)
        if not bucket:
            print("ERROR: No bucket configured.")
            return 2

        key = f"connectivity_test/{int(time.time())}_presign.txt"
        body = f"presigned url probe at {datetime.utcnow().isoformat()}Z\n"

        # Upload the probe file
        s3.put_object(Bucket=bucket, Key=key, Body=body.encode('utf-8'))

        # Generate a presigned URL valid for 15 minutes
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=900
        )

        print("Bucket:", bucket)
        print("Key:", key)
        print("PresignedURL:", url)
        return 0
    except NoCredentialsError:
        print("ERROR: No AWS credentials found.")
        return 3
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code')
        print(f"ERROR: AWS ClientError {code}: {e}")
        return 4
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())










