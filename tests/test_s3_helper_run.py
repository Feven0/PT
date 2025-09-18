import os
import tempfile

from api.utils import s3_client


def pick_bucket() -> str:
    buckets = s3_client.list_buckets()
    print("Buckets (first 10):", buckets[:10])
    preferred = "tenx-parrot-assets"
    if preferred in buckets:
        print(f"Using preferred bucket: {preferred}")
        return preferred
    return "The bucket is not found"


def test_get_s3_client():
    cli = s3_client.get_s3_client()
    # Simple call to verify client works
    _ = cli.list_buckets()
    print("get_s3_client(): OK")


def test_list_buckets():
    buckets = s3_client.list_buckets()
    assert isinstance(buckets, list)
    print("list_buckets():", len(buckets), "buckets")


def test_upload_file_and_get_url(bucket: str):
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write("hello from upload_file_and_get_url\n")
        tf.flush()
        path = tf.name

    url, key = s3_client.upload_file_and_get_url(bucket, path)
    print("upload_file_and_get_url():", url, key)
    os.remove(path)


def test_upload_bytes_and_get_url(bucket: str):
    data = b"hello from upload_bytes_and_get_url\n"
    url, key = s3_client.upload_bytes_and_get_url(bucket, data)
    print("upload_bytes_and_get_url():", url, key)


def main():
    test_get_s3_client()
    test_list_buckets()
    bucket = pick_bucket()
    test_upload_file_and_get_url(bucket)
    test_upload_bytes_and_get_url(bucket)
    print("All tests finished.")


if __name__ == "__main__":
    main()


