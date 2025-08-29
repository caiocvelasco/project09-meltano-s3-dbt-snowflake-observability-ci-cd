# Meltano Data Ingestion Pipeline

This directory contains a Meltano project for extracting data from Stripe and loading it directly to AWS S3.

## Overview

This pipeline extracts data from Stripe (payments, customers, events, etc.) and loads it directly to S3 using Meltano's native S3 loader. **No custom scripts are required** - Meltano handles the complete pipeline from extraction to S3 upload.

## Prerequisites

- Python 3.8+ with virtual environment
- AWS CLI configured with appropriate credentials
- Stripe account with API access
- S3 bucket for data storage

## Setup Instructions

### 1. Initialize Meltano Project

```bash
# Navigate to the ingestion directory
cd ingestion

# Initialize Meltano project
# This command creates a new Meltano project in the current directory
# It generates the initial meltano.yml configuration file and project structure
meltano init .
```

### 2. Install Plugins

**Why Plugins are Necessary:**
Meltano uses a plugin architecture where:
- **Extractors (taps)**: Connect to data sources and extract data in a standardized format
- **Loaders (targets)**: Receive the extracted data and load it into destination systems
- **Transformers**: Optional components that transform data between extraction and loading

**Plugins We'll Add and Why:**

#### Add Stripe Extractor
**Why tap-stripe:**
- Extracts data from Stripe's API (payments, customers, events, etc.)
- Provides standardized Singer-compatible output format
- Handles authentication, pagination, and incremental extraction
- Supports multiple Stripe endpoints in a single extraction
```bash
# Add tap-stripe extractor
meltano add extractor tap-stripe
```

#### Add S3 CSV Loader
**Why target-s3-csv:**
- **Loads data directly to S3** without intermediate files
- **Creates properly timestamped CSV files** in S3
- **Supports all data types** and nested structures
- **Handles folder structure** and naming conventions
- **No custom scripts required** - pure Meltano solution

```bash
# Add target-s3-csv loader
meltano add loader target-s3-csv
```

**Note**: You may see installation warnings on Windows due to path length limitations, but the plugin will work correctly despite these warnings.

### 3. Install All Plugins

**Why Install All Plugins:**
After adding plugins to the configuration, we need to install them to:
- **Download and install the actual Python packages** for each plugin
- **Resolve dependencies** between plugins and their requirements
- **Make plugins executable** within the Meltano environment
- **Ensure version compatibility** between extractors and loaders
- **Create the plugin execution environment** for the data pipeline

```bash
# Install all configured plugins
meltano install
```

### 4. Configure Plugins

#### Configure S3 CSV Loader
```bash
# Set S3 bucket
meltano config target-s3-csv set s3_bucket s3-observability-project

# Set S3 key prefix for folder structure
meltano config target-s3-csv set s3_key_prefix raw/stripe/
```

#### Configure Stripe Extractor

Update the `meltano.yml` file with your Stripe configuration using environment variables:

```yaml
extractors:
- name: tap-stripe
  variant: singer-io
  pip_url: git+https://github.com/singer-io/tap-stripe.git
  config:
    client_secret: $TAP_STRIPE_CLIENT_SECRET
    account_id: $TAP_STRIPE_ACCOUNT_ID
    start_date: '2025-08-25'  # Use today's date for fresh extraction
```

**Important Note**: The `account_id` should come from **Stripe Dashboard > Settings > Business Settings**, not from Personal Details. This is the business account ID that identifies your Stripe Connect platform or business account.

**Security Note**: This approach uses environment variables from your `.env` file, keeping sensitive credentials secure and out of version control.

### 5. Environment Variables Setup

Create a `.env` file in the `ingestion/` directory with your Stripe credentials:

```bash
# Stripe API Configuration
TAP_STRIPE_CLIENT_SECRET=sk_test_your_actual_stripe_secret_key
TAP_STRIPE_ACCOUNT_ID=acct_your_actual_stripe_account_id
```

**How to get your Stripe credentials:**
1. Go to your Stripe Dashboard (https://dashboard.stripe.com/)
2. Make sure you're in **Test mode** (toggle in the top right)
3. Go to **Developers** → **API keys**
4. Copy your **Secret key** (starts with `sk_test_`)
5. Copy your **Account ID** (starts with `acct_`)

### 6. AWS CLI Configuration (for S3 access)

Ensure AWS CLI is configured with credentials that have S3 access:

```bash
# Check AWS configuration
aws configure list

# Test S3 access
aws s3 ls s3://s3-observability-project
```

If you need to set up AWS credentials, run:
```bash
aws configure set aws_access_key_id YOUR_ACCESS_KEY --profile default
aws configure set aws_secret_access_key YOUR_SECRET_KEY --profile default
aws configure set region eu-north-1 --profile default
aws configure set output json --profile default
```

## Running the Pipeline

### Complete End-to-End Pipeline

**The beauty of Meltano is that it handles everything in one command:**

```bash
# Run the complete pipeline: extract from Stripe → load directly to S3
meltano run tap-stripe target-s3-csv
```

**What happens automatically:**
- ✅ **Extracts data** from all configured Stripe streams
- ✅ **Creates timestamped CSV files** in S3
- ✅ **Handles folder structure** automatically
- ✅ **No intermediate files** or manual uploads needed
- ✅ **Incremental updates** work seamlessly

**Note**: On Windows, use `meltano run` instead of `meltano elt` as the `elt` command is not supported on Windows.

### Verify Plugin Configuration

```bash
# Check tap-stripe configuration
meltano config tap-stripe list

# Check target-s3-csv configuration
meltano config target-s3-csv list

# Test individual plugins
meltano invoke tap-stripe --help
meltano invoke target-s3-csv --help
```

### Data Extraction Summary

The pipeline extracts data from multiple Stripe endpoints:
- **charges**: Payment charges
- **events**: Stripe webhook events
- **customers**: Customer records
- **products**: Product catalog
- **invoices**: Invoice data
- **subscriptions**: Subscription data
- **disputes**: Payment disputes
- **payouts**: Account payouts
- And more...

## S3 Output Structure

### Automatic S3 Organization

Meltano automatically creates properly organized files in S3:

```
s3://s3-observability-project/raw/stripe/
├── balance_transactions-20250825T175828.csv
├── charges-20250825T175828.csv
├── customers-20250825T175828.csv
├── events-20250825T175828.csv
└── payment_intents-20250825T175828.csv
```

### File Naming Convention

Files are automatically named with:
- **Stream name**: The Stripe endpoint (charges, events, etc.)
- **Timestamp**: When the data was extracted (YYYYMMDDTHHMMSS format)
- **Format**: CSV files for easy processing

### Data Processing

**What the pipeline extracts:**
- **32 events** (32 new, 0 updates) 
- **14 charges** (7 new, 7 updates)
- **8 customers** (4 new, 4 updates)
- **14 payment_intents** (7 new, 7 updates)
- **5 balance_transactions** (5 new, 0 updates)

**Why Some Files Might Not Appear:**
- **Empty Streams**: If a Stripe endpoint has no data, no file will be created
- **Test Account**: New Stripe test accounts may not have charges, customers, or other data
- **Date Range**: The `start_date` configuration affects which data is extracted

## Verification

### Check S3 Upload

```bash
# List all files in the raw directory
aws s3 ls s3://s3-observability-project/raw/stripe/ --recursive

# Download a sample file to inspect
aws s3 cp s3://s3-observability-project/raw/stripe/charges-20250825T175828.csv ./sample-charges.csv
```

### Pipeline Logs

Meltano provides detailed logging including:
- API request/response details
- Record counts per endpoint
- Performance metrics
- Error handling
- Incremental sync status

## Troubleshooting

### Common Issues

1. **"meltano: command not found"**
   - Ensure virtual environment is activated: `source .venv/Scripts/activate`

2. **"Must be run inside a Meltano project"**
   - Ensure you're in the `ingestion/` directory with `meltano.yml`

3. **AWS credentials not found**
   - Configure AWS CLI: `aws configure`
   - Test access: `aws s3 ls`

4. **Stripe authentication errors**
   - Verify API keys in `.env` file
   - Check account_id for Connect platforms

5. **Windows compatibility issues**
   - Use `meltano run` instead of `meltano elt` (Windows compatibility)
   - Ensure plugins are properly installed with `meltano install`

6. **Plugin installation warnings**
   - **Windows path length warnings are normal** and don't affect functionality
   - The plugins work correctly despite these warnings
   - Test with `meltano invoke target-s3-csv --help` to verify installation

### Plugin Installation on Windows

If you encounter path-related installation warnings:

```bash
# These warnings are normal on Windows and don't affect functionality
# Test that the plugin actually works:
meltano invoke tap-stripe --help
meltano invoke target-s3-csv --help

# If the help commands work, the plugin is functional
```

## Configuration Files

### meltano.yml
Main configuration file containing:
- Plugin definitions
- Extractor/loader settings
- Pipeline configurations
- Environment configurations

#### Meltano Environments
Meltano supports multiple environments for different deployment stages:

- **dev**: Development environment for testing and development work
- **staging**: Pre-production environment for testing before production deployment
- **prod**: Production environment for live data processing

**Why Multiple Environments?**
- **Isolation**: Separate configurations for different stages of development
- **Testing**: Safe testing of new configurations without affecting production
- **Security**: Different credentials and settings for each environment
- **Deployment**: Gradual rollout from development → staging → production

### Environment Variables (.env files)

This project uses environment variables for secure credential management:

#### Ingestion Folder `.env` (./.env)
Contains Meltano-specific environment variables:
```
TAP_STRIPE_CLIENT_SECRET=sk_test_...
TAP_STRIPE_ACCOUNT_ID=acct_...
```

**Security Benefits:**
- **Secure**: Credentials are kept out of version control
- **Flexible**: Easy to change credentials without modifying code
- **Environment-specific**: Different credentials for different environments

## Complete Workflow Example

Here's the complete workflow from start to finish:

```bash
# 1. Activate virtual environment
source ../.venv/Scripts/activate

# 2. Run complete Meltano pipeline (extract + load to S3)
meltano run tap-stripe target-s3-csv

# 3. Verify S3 upload
aws s3 ls s3://s3-observability-project/raw/stripe/ --recursive
```

**That's it!** No custom scripts, no manual uploads, no intermediate files. Meltano handles everything automatically.

## Step-by-Step Data Ingestion Guide

Once your setup is complete, here's how to ingest data:

### 1. Prepare Your Environment

```bash
# Navigate to the ingestion directory
cd ingestion

# Activate your virtual environment
source ../.venv/Scripts/activate

# Verify your environment is ready
meltano --version
```

### 2. Verify Configuration

```bash
# Check that your plugins are properly configured
meltano config tap-stripe list
meltano config target-s3-csv list

# Verify your .env file exists and has the right variables
ls -la .env
```

### 3. Run Data Ingestion

```bash
# Execute the complete pipeline
meltano run tap-stripe target-s3-csv
```

**What this does:**
- Connects to Stripe API using your credentials
- Extracts all available data from configured streams
- Automatically uploads CSV files to S3
- Creates timestamped files in the correct folder structure

### 4. Verify the Results

```bash
# Check what files were uploaded to S3
aws s3 ls s3://s3-observability-project/raw/stripe/ --recursive

# Download a sample file to inspect the data
aws s3 cp s3://s3-observability-project/raw/stripe/events-*.csv ./sample-events.csv
head -5 sample-events.csv
```

### 5. Monitor the Logs

The pipeline provides detailed logs showing:
- Number of records extracted from each stream
- API request/response details
- Upload progress to S3
- Any errors or warnings

### 6. For Fresh Data Extraction (Full Refresh)

If you want to extract all data from scratch (ignoring incremental state):

```bash
# Remove the Meltano state to force a complete fresh extraction
rm -rf .meltano/run/tap-stripe/

# Clear existing S3 files (optional)
aws s3 rm s3://s3-observability-project/raw/stripe/ --recursive

# Run the extraction again
meltano run tap-stripe target-s3-csv
```

### 7. Schedule Regular Ingestion

For automated data ingestion, you can:

**Option A: Use Cron (Linux/Mac)**
```bash
# Add to crontab to run every hour
0 * * * * cd /path/to/ingestion && source ../.venv/Scripts/activate && meltano run tap-stripe target-s3-csv
```

**Option B: Use Windows Task Scheduler**
- Create a batch file with the ingestion command
- Schedule it to run at your desired frequency

**Option C: Use CI/CD Pipeline**
- Add the ingestion command to your CI/CD pipeline
- Run it on schedule or on-demand

### 8. Troubleshooting Ingestion Issues

**If you get no data:**
```bash
# Check if your Stripe account has data
# Verify your API keys are correct
# Ensure your start_date is appropriate

# Test the connection
meltano invoke tap-stripe --help
```

**If you get partial data:**
```bash
# Check the logs for any errors
# Verify your Stripe account has the expected data
# Consider running a full refresh (step 6)
```

**If S3 upload fails:**
```bash
# Verify AWS credentials
aws s3 ls s3://s3-observability-project

# Check S3 bucket permissions
# Ensure the bucket exists and is accessible
```

## Key Benefits of This Approach

### ✅ **Pure Meltano Solution**
- **No custom scripts required** - everything is handled by Meltano plugins
- **Standardized approach** - uses well-maintained, tested plugins
- **Easy maintenance** - no custom code to maintain or debug

### ✅ **Automatic File Management**
- **Timestamped files** - automatic naming with extraction timestamps
- **Proper folder structure** - organized in S3 with correct prefixes
- **Incremental updates** - only new/changed data is processed

### ✅ **Production Ready**
- **Error handling** - built-in retry logic and error reporting
- **Logging** - comprehensive logs for monitoring and debugging
- **Scalable** - can handle large datasets efficiently

### ✅ **Cross-Platform**
- **Windows compatible** - works despite installation warnings
- **Linux/Mac ready** - same commands work across platforms
- **Cloud friendly** - designed for cloud deployment

## Next Steps

1. **Schedule the pipeline**: Set up automated runs using cron or CI/CD
2. **Add more extractors**: Connect additional data sources
3. **Data transformation**: Use dbt for data modeling and transformation
4. **Monitoring**: Set up alerts and observability
5. **Data warehouse**: Load processed data into Snowflake/BigQuery

## Resources

- [Meltano Documentation](https://docs.meltano.com/)
- [tap-stripe Documentation](https://hub.meltano.com/extractors/tap-stripe)
- [target-s3-csv Documentation](https://hub.meltano.com/loaders/target-s3-csv--transferwise)
- [Stripe API Documentation](https://stripe.com/docs/api)

