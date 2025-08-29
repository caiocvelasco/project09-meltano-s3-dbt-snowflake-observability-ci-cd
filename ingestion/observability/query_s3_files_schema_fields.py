from dotenv import load_dotenv
import boto3
import os
import sys
from collections import defaultdict
from io import StringIO
import csv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME") or "s3-observability-project"
S3_PREFIX = os.getenv("S3_PREFIX", "raw/stripe/")
AWS_REGION = os.getenv("AWS_REGION") or os.getenv("S3_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("S3_SECRET_ACCESS_KEY")

if not S3_BUCKET:
    print("S3 bucket env var not set")
    sys.exit(1)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def main():
    print(f"Listing under s3://{S3_BUCKET}/{S3_PREFIX}")
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
    if "Contents" not in resp:
        print("No files found")
        return

    by_stream = defaultdict(list)
    for obj in resp["Contents"]:
        key = obj["Key"]
        base = key.split("/")[-1]
        stream = base.split("-")[0] if "-" in base else base.split(".")[0]
        by_stream[stream].append(obj)

    for stream in sorted(by_stream.keys()):
        latest = max(by_stream[stream], key=lambda o: o["LastModified"])  # type: ignore
        key = latest["Key"]
        print(f"\n=== Stream: {stream} | Key: {key} ===")
        body = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            text = body.decode("latin-1", errors="replace")

        # Prefer CSV: parse headers
        try:
            csvfile = StringIO(text)
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames or []
            if headers:
                print("Fields (CSV):")
                print(", ".join(headers))
                continue
        except Exception:
            pass

        # Not CSV or no headers
        print("Not a CSV or headers could not be determined.")


if __name__ == "__main__":
    main()
