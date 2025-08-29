# This script is our first observability check:
# Does S3 (under the prefix defined (raw/stripe/)) contain the files that were produced by your Meltano → tap-stripe → target-s3-csv ingestion step?
# Are those files non-empty?


from dotenv import load_dotenv
import boto3
import os
import sys

# Load .env file
load_dotenv()

# Map your .env variables
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "raw/stripe/")
AWS_REGION = os.getenv("S3_REGION")
AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")

if not S3_BUCKET:
    print("S3_BUCKET_NAME environment variable is required")
    sys.exit(1)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def check_files():
    print(f"Checking s3://{S3_BUCKET}/{S3_PREFIX}")
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
    if "Contents" not in response:
        print(f"No files found in s3://{S3_BUCKET}/{S3_PREFIX}")
        return False

    all_good = True
    for obj in response["Contents"]:
        size = obj["Size"]
        key = obj["Key"]
        print(f"File: {key}")
        if size == 0:
            print(f"WARN File is empty: {key}")
            all_good = False
        else:
            print(f"- OK File exists: {key} ({size} bytes)")
    return all_good

if __name__ == "__main__":
    success = check_files()
    sys.exit(0 if success else 1)
