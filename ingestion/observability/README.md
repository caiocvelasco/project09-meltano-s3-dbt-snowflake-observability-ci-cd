## Observability for raw/stripe

### Overview
- This folder contains lightweight checks for the raw S3 layer produced by Meltano (tap-stripe → target-s3-csv).
- Scripts are ordered to reflect the logical workflow:
  - query_s3_files_schema_fields.py: Explore fields actually present in S3 CSVs (per stream)
  - 01_check_s3_files.py: Existence/size checks for S3 objects
  - 02_check_s3_schema.py: Schema drift checks (required fields per stream)

### Prerequisites
- Python venv for the project is already set up and activated
- Packages: boto3, python-dotenv
- Environment variables (via .env or exported):
  - S3_BUCKET_NAME=s3-observability-project
  - S3_PREFIX=raw/stripe/
  - AWS_REGION (or S3_REGION)
  - AWS_ACCESS_KEY_ID (or S3_ACCESS_KEY_ID)
  - AWS_SECRET_ACCESS_KEY (or S3_SECRET_ACCESS_KEY)

### How to run
- From this folder:
  - Print current CSV headers per latest file per stream (flattened column list):
    ```bash
    python query_s3_files_schema_fields.py
    ```
  - Check file presence and non-empty size under the prefix:
    ```bash
    python 01_check_s3_files.py
    ```
  - Validate required fields per stream (schema drift guard):
    ```bash
    python 02_check_s3_schema.py
    ```
  - Run both checks together:
    ```bash
    ./run_checks.sh
    ```

### What each script does
- query_s3_files_schema_fields.py
  - Lists the latest object per stream under `s3://$S3_BUCKET_NAME/$S3_PREFIX`
  - Parses the CSV header and prints the full, flattened field list
- 01_check_s3_files.py
  - Lists objects under the prefix and reports empty or missing files
- 02_check_s3_schema.py
  - Validates that CSV (or JSON) files contain required fields per stream.
  - Streams validated: `charges`, `events`, `customers`, `payment_intents` (others default to `id`, `created`).
  - Matching rule for flattened fields: a required field passes if there is an exact column match OR a column starting with `field__` (e.g., `payment_method_details` matches `payment_method_details__card__brand`).

### Answers to common questions
- tap-stripe configuration (from ingestion/meltano.yml)
  - Configured with client_secret, account_id, and start_date
  - No explicit stream or field selections are defined in meltano.yml
  - Example snippet:
    ```yaml
    extractors:
    - name: tap-stripe
      variant: singer-io
      pip_url: git+https://github.com/singer-io/tap-stripe.git
      config:
        client_secret: $TAP_STRIPE_CLIENT_SECRET
        account_id: $TAP_STRIPE_ACCOUNT_ID
        start_date: '2025-08-25'
    loaders:
    - name: target-s3-csv
      variant: transferwise
      pip_url: git+https://github.com/transferwise/pipelinewise-target-s3-csv.git
      config:
        s3_bucket: s3-observability-project
        s3_key_prefix: raw/stripe/
        naming_convention: '{stream}-{timestamp}.csv'
    ```
- Which streams/fields are enabled?
  - No selections are pinned in meltano.yml. tap-stripe discovery provides available streams; you can pin with `meltano select` if desired.
- How does state (incremental) work?
  - Incremental extraction is managed by tap-stripe (Singer) using replication keys like `created` and the configured `start_date`
  - Meltano persists state at `.meltano/run/tap-stripe/state.json`
  - Full refresh: delete that file or run `meltano state clear tap-stripe`
- Are there transform plugins changing field names?
  - No transform plugins are configured for this ingestion in meltano.yml
  - Flattened column names (e.g., `billing_details__address__city`) come from the loader’s JSON→CSV conversion
- Which loader is used?
  - `target-s3-csv` (variant `transferwise` / `pipelinewise-target-s3-csv`) uploads CSVs directly to S3

### Interpreting flattened fields
- Nested JSON fields are flattened using `__` separators, producing columns like:
  - charges: `billing_details__address__city`, `payment_method_details__card__brand`
  - events: `data__object__amount`, `data__object__latest_charge`, `data__object__payment_method_types`
  - customers: `shipping__address__city`, `invoice_settings__default_payment_method`
  - payment_intents: `payment_method_options__card__installments`, `payment_method_types`

### References
- Loader: pipelinewise-target-s3-csv (archived repo): `https://github.com/transferwise/pipelinewise-target-s3-csv`
- Stripe object docs for field meanings:
  - Charges: `https://docs.stripe.com/api/charges/object`
  - Events: `https://docs.stripe.com/api/events/object`
  - Customers: `https://docs.stripe.com/api/customers/object`
  - Payment Intents: `https://docs.stripe.com/api/payment_intents/object`
  - Balance Transactions: `https://docs.stripe.com/api/balance_transactions/object`



