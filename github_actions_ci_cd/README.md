# Stripe Observability & Meltano Ingestion GitHub Actions

This folder contains **GitHub Actions workflows** that automate the ingestion and validation of Stripe data into S3, ensuring reliable data pipelines, early detection of schema drift, and a fully automated CI/CD process.

---

## Workflows Overview

### 1. Observability Workflow (CI)

- **Purpose:** Validates that Stripe ingestion files exist in S3 and their schema matches expectations.
- **Trigger:** 
  - On every push to the `main` branch (optional, can be disabled if only scheduled runs are needed).
  - Manually via **workflow dispatch**.
- **Jobs:** `check-schema`

#### Steps:

1. **Checkout repository**  
   Uses `actions/checkout@v3` to pull the latest code.

2. **Set up Python 3.11**  
   Uses `actions/setup-python@v4`.

3. **Cache pip dependencies**  
   Speeds up workflow execution.

4. **Install dependencies**  
   Installs required packages from `requirements-observability.txt`.

5. **Run S3 File Existence Check**  
   Executes `01_check_s3_files.py` to verify the presence of expected files.

6. **Run S3 Schema Drift Check**  
   Executes `02_check_s3_schema.py` to validate CSV schema for each Stripe stream (charges, events, customers, refunds, etc.).

---

### 2. Meltano Ingestion Workflow (CD)

- **Purpose:** Automates the ingestion of Stripe data into S3 on a schedule.
- **Trigger:**  
  - Scheduled daily at 23:00 Europe/Madrid (21:00 UTC).  
  - Manually via **workflow dispatch**.
- **Jobs:** `meltano-ingestion`

#### Steps:

1. **Checkout repository**  
   Pulls the latest code.

2. **Set up Python 3.11**  
   Ensures correct Python environment.

3. **Cache pip dependencies**  
   Reuses installed packages to speed up workflow.

4. **Create virtual environment & install Meltano dependencies**  
   Installs only `meltano` and its plugin requirements from `requirements-meltano.txt`.

5. **Install Meltano plugins**  
   Runs `meltano install` inside the `ingestion/` folder to ensure all extractors/loaders are available.

6. **Run Meltano ingestion**  
   Executes `meltano run tap-stripe target-s3-csv` inside the `ingestion/` folder to ingest Stripe data into S3.

---

## Environment Variables / Secrets

Both workflows rely on GitHub secrets mapped to environment variables:

- `S3_BUCKET_NAME`
- `S3_REGION`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `TAP_STRIPE_CLIENT_SECRET`
- `TAP_STRIPE_ACCOUNT_ID`
- `OBS_STREAMS` (comma-separated list of Stripe streams, e.g., `charges,events,customers,refunds`)

These are injected automatically during workflow runs.

---

## Python Scripts (Observability)

Located in `ingestion/observability/`:

### 1. `01_check_s3_files.py`

- Validates the existence of expected S3 files.
- Exits with **code 1** if any files are missing.

### 2. `02_check_s3_schema.py`

- Checks CSV schema against expected Stripe fields.
- Handles flattened nested fields (e.g., `payment_method_details__card__brand`).
- Logs warnings for missing fields.
- Exits with **code 1** if any schema violations are found.

---

## CI/CD Summary

- **CI:** Observability workflow ensures ingestion files exist and schemas are correct.
- **CD:** Meltano workflow automates daily ingestion from Stripe to S3.
- Together, they form a **complete CI/CD pipeline for your Stripe data ingestion**.
- Future enhancement: trigger **dbt transformations** after Meltano ingestion for a full **ingest → transform → validate** workflow.

---

## Folder Structure

```
.github/
└─ workflows/
├─ stripe_observability.yml
└─ meltano_ingestion.yml

ingestion/
├─ observability/
│ ├─ 01_check_s3_files.py
│ ├─ 02_check_s3_schema.py
│ ├─ query_s3_files_schema_fields.py
│ └─ run_checks.sh
├─ meltano.yml
├─ requirements.txt
└─ README.md

```
## Notes

- Workflows run in **clean GitHub VMs**, so all dependencies must be installed in the workflow environment.
- Observability workflow is lightweight and safe to run frequently.
- Meltano ingestion workflow handles production data ingestion and should be scheduled carefully.
- Secrets management ensures sensitive credentials are never exposed.
