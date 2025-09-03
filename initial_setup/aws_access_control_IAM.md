# Access Control Setup for AWS ↔️ Snowflake Storage Integration

This document explains how to configure **IAM Users, Groups, Roles, and Policies** in AWS, and connect them securely with **Snowflake Storage Integrations**.  
This ensures that Snowflake can read CSV files from your S3 bucket (`s3-observability-project`) while following best practices in access control.

---

## Step 0: Prerequisites

- AWS Account with an existing S3 bucket (e.g., `s3-observability-project`)
- Snowflake account with sufficient privileges to create integrations
- Snowflake ingestion user (e.g., `DBT_USER`)
- Access to AWS Console → IAM
- You know your Snowflake **Account ID** and will later retrieve an **External ID** via `DESC INTEGRATION`.

---

## Step 1: Create IAM Group with S3 Access Policy

1. Go to **IAM → Groups → Create group**.  
2. Name: `meltano-ingestion-group`.  
3. Create a **custom inline policy** called `my-s3-observability-project-bucket` with this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::s3-observability-project"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::s3-observability-project/*"]
    }
  ]
}

```
4. Attach the policy to the group.

## Step 2: Create IAM User for Ingestion

1. Go to IAM → Users → Add user.
2. Name: meltano-ingest-user.
3. Select **Programmatic access** (not console).
4. Add this user to the group meltano-ingestion-group.
5. Save the **Access Key** and **Secret Key** (you will need them for Meltano / ingestion scripts).

At this point:

- meltano-ingest-user can read/write to the bucket for ingestion.
- This covers your **ETL/Meltano ingestion side**.

## SStep 3: Create IAM Policy for Snowflake Role

Snowflake needs its own IAM Role with access to the same S3 bucket. Create a separate policy `snowflake-s3-access` with the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::s3-observability-project"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::s3-observability-project/*"]
    }
  ]
}
```

## Step 4: Create IAM Role for Snowflake Storage Integration

1. Go to **IAM → Roles → Create role**.
2. Choose **Another AWS Account**.
3. Enter the **Snowflake AWS Account ID** (you get this from Snowflake after creating the integration and running DESC INTEGRATION).
4. Check **Require external ID** and paste the `STORAGE_AWS_EXTERNAL_ID` value from Snowflake.
5. Name the role: `snowflake-observability-role`.
6. Attach the policy `snowflake-s3-access` created in Step 3.


## Step 5: Update Role Trust Policy

Replace the trust policy of the role with the following (values must match your Snowflake account + external ID):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::694318440714:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "IW52833_SFCRole=2_QCZ9fyLR4h0ACvQH2Si9Q335t7Y="
        }
      }
    }
  ]
}
```
- Replace `694318440714` with the Snowflake AWS Account ID shown in `DESC INTEGRATION`.
- Replace the `sts:ExternalId` with your Snowflake integration’s external ID.

## Step 6: Create Snowflake Storage Integration

```sql
CREATE OR REPLACE STORAGE INTEGRATION OBS_S3_INTEGRATION
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::286218346471:role/snowflake-observability-role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://s3-observability-project');
```

Grant usage to your ingestion role:

```sql
GRANT USAGE ON INTEGRATION OBS_S3_INTEGRATION TO ROLE INGEST_TRANSFORM_ROLE;
```

## Step 7: Verify Integration

Run in Snowflake:

```sql
DESC INTEGRATION OBS_S3_INTEGRATION;
```

Check the values for:

- STORAGE_AWS_IAM_USER_ARN

- STORAGE_AWS_EXTERNAL_ID

⚠️ These must match the AWS Role trust policy. If they don’t, update the IAM Role trust policy accordingly.

---

At this point:

## Final State

- ETL ingestion user (meltano-ingest-user) can push data to S3.
- Snowflake integration role (snowflake-observability-role) allows Snowflake to securely assume permissions and read from S3.
- Snowflake integration (OBS_S3_INTEGRATION) links Snowflake to the IAM Role.
- Stages & file formats in Snowflake allow external tables and dbt models to consume the data.