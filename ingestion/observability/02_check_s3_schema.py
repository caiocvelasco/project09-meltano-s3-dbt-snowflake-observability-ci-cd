# Schema Drift Check for Stripe data in S3
#
# This script validates that ingested files in S3 contain the expected fields.
# It helps detect schema drift (missing or renamed fields), including flattened nested fields.
#
# Runs as a GitHub Action on the `main` branch.
#

from dotenv import load_dotenv
import boto3
import os
import sys
import json
import csv
from io import StringIO
import os.path as op

# Load environment variables from .env (only for local testing; GitHub Actions passes them directly)
load_dotenv()

# S3 configuration from environment variables
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "raw/stripe/")

# Boto3 S3 client using secrets / env vars
s3 = boto3.client(
    "s3",
    region_name=os.getenv("S3_REGION"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
)

# Expected fields per Stripe stream (business requirement)
# Nested objects will be flattened in CSV as field__subfield
REQUIRED_BY_STREAM = {
    "charges": ["id", "created", "status", "customer", "refunded", "amount", "amount_captured", "amount_refunded", "payment_method_details"],
    "events": ["id", "created", "type", "data"],
    "customers": ["id", "created", "email", "name", "phone", "address", "shipping", "balance", "currency", "tax_exempt"],
    "payment_intents": ["id", "amount", "created", "status", "customer", "latest_charge", "next_action", "payment_method"],
}

DEFAULT_REQUIRED = ["id", "created"]

def check_stripe_json_per_csv_stream(file_bytes, expected_stripe_fields, s3_filename):
    """
    Validate that a JSON file (representing a Stripe stream CSV ingestion) contains all required fields.
    Returns True if all required fields are present, False otherwise.
    """
    stripe_entries = json.loads(file_bytes)
    if isinstance(stripe_entries, dict):
        stripe_entries = [stripe_entries]
    all_good = True
    for entry in stripe_entries:
        for field in expected_stripe_fields:
            if field not in entry:
                print(f"WARN Missing expected Stripe field '{field}' in {s3_filename}")
                all_good = False
    if all_good:
        print(f"OK JSON file '{s3_filename}' passed schema validation for all objects")
    return all_good

def check_stripe_csv_per_stream(file_bytes, expected_stripe_fields, s3_filename):
    """
    Validate that a CSV file (representing a Stripe stream ingestion) contains all required fields.
    Handles flattened nested objects (e.g., payment_method_details__card__brand)
    Returns True if all required fields are present, False otherwise.
    """
    try:
        csv_file = StringIO(file_bytes.decode("utf-8"))
        csv_reader = csv.DictReader(csv_file)
        actual_fields = csv_reader.fieldnames

        all_good = True
        for field in expected_stripe_fields:
            # Accept the field if any CSV column matches exactly or starts with field + "__"
            if not any(f == field or f.startswith(field + "__") for f in actual_fields):
                print(f"WARN Missing expected Stripe field '{field}' in {s3_filename}")
                all_good = False

        if all_good:
            print(f"OK CSV file '{s3_filename}' passed schema validation")
        return all_good
    except Exception as e:
        print(f"Error reading {s3_filename}: {e}")
        return False

def check_all_files_in_s3():
    """
    Iterate over S3 objects under the specified prefix, detect stream type,
    and validate schema (JSON first, then CSV).
    """
    print(f"Listing files in s3://{S3_BUCKET}/{S3_PREFIX}")
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
    if "Contents" not in response:
        print("No files found in S3")
        return False

    all_good = True
    print(f"Found {len(response['Contents'])} files in S3 folder")

    for obj in response["Contents"]:
        s3_filename = obj["Key"]
        print(f"\nProcessing file: {s3_filename}")
        base = op.basename(s3_filename)
        stream = base.split("-")[0] if "-" in base else base.split(".")[0]
        expected_fields = REQUIRED_BY_STREAM.get(stream, DEFAULT_REQUIRED)
        print(f"Detected stream: {stream}, expected fields: {expected_fields}")

        file_bytes = s3.get_object(Bucket=S3_BUCKET, Key=s3_filename)["Body"].read()

        # Try JSON validation first, then fallback to CSV
        try:
            if not check_stripe_json_per_csv_stream(file_bytes, expected_fields, s3_filename):
                all_good = False
        except json.JSONDecodeError:
            print(f"File '{s3_filename}' is not JSON, trying CSV validation")
            if not check_stripe_csv_per_stream(file_bytes, expected_fields, s3_filename):
                all_good = False

    return all_good

if __name__ == "__main__":
    print("Starting Stripe schema drift check...\n")
    success = check_all_files_in_s3()
    if success:
        print("\nAll files passed schema validation ✅")
    else:
        print("\nSome files failed schema validation ❌")
    sys.exit(0 if success else 1)
