# Stripe Observability GitHub Actions

This folder contains a **GitHub Actions workflow** that automates validation of Stripe ingestion data stored in S3. It ensures that files are present and that their schema matches expectations, helping detect **data ingestion issues** or **schema drift** early.

---

## Workflow Overview

### Trigger

The workflow runs:

- On every push to the `main` branch.
- Manually via **workflow dispatch**.

### Jobs

#### 1. `check-schema`

- **Runs on**: `ubuntu-latest`
- **Environment variables**: Mapped from GitHub secrets for secure access to S3 and Stripe credentials.

**Steps:**

1. **Checkout repository**  
   Uses `actions/checkout@v3` to pull the latest code.

2. **Set up Python**  
   Uses `actions/setup-python@v4` with Python 3.11.

3. **Cache pip**  
   Caches dependencies to speed up workflow runs.

4. **Install dependencies**  
   Installs required Python packages from the root `requirements.txt`.

5. **Run S3 File Existence Check**  
   Executes `01_check_s3_files.py` to verify that expected files exist in the S3 bucket.

6. **Run S3 Schema Drift Check**  
   Executes `02_check_s3_schema.py` to validate that CSV files match the expected Stripe schema for each stream (charges, events, customers, etc.).

---

## Environment Variables / Secrets

The workflow uses the following **GitHub secrets** (configured in your repository settings):

- `S3_BUCKET_NAME`
- `S3_REGION`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `TAP_STRIPE_CLIENT_SECRET`
- `TAP_STRIPE_ACCOUNT_ID`
- `OBS_STREAMS` (comma-separated list of Stripe streams, e.g., `charges,events,customers,refunds`)

These map to Python environment variables automatically during the workflow run.

---

## Python Scripts

### 1. `01_check_s3_files.py`

Checks that files exist in S3 under the configured prefix (`raw/stripe/`).  
Exits with **code 1** if any files are missing.

### 2. `02_check_s3_schema.py`

Validates the CSV schema of ingested Stripe files.  
- Handles flattened nested fields (e.g., `payment_method_details__card__brand`)  
- Warns if required fields are missing.  
- Exits with **code 1** if any files fail validation.

---

## Notes

- This is a **CI workflow**, not full CI/CD.  
- Dependencies are installed fresh in the workflow environment for each run to mimic the local setup.  
- GitHub Actions runs in a clean VM, so local `.venv` or global Python packages are not available.  
- You can extend this workflow to **trigger Meltano or dbt pipelines** after passing validation for a full CI/CD pipeline.

---

## Folder Structure

