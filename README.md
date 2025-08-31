# Data Engineering Project: Meltano + S3 + dbt + Snowflake + Observability + CI/CD

A comprehensive data engineering project demonstrating modern data pipeline architecture with automated ingestion, transformation, and observability.

## 🎯 Project Overview

This project implements a complete data pipeline from data ingestion to transformation and observability:

1. **Data Ingestion** - Meltano extracts data from Stripe and loads to S3
2. **CI/CD Pipeline** - GitHub Actions automate ingestion and validation
3. **Data Transformation** - dbt transforms data in Snowflake (in progress)
4. **Observability** - Automated schema validation and data quality checks

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Current Progress](#current-progress)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Initiate the Environment](#initiate-the-environment)
- [Data Ingestion Pipeline](#data-ingestion-pipeline)
- [CI/CD Pipeline](#cicd-pipeline)
- [Data Transformation (dbt + Snowflake)](#data-transformation-dbt--snowflake)
- [Next Steps](#next-steps)

## 🏗️ Project Structure

```
project09-meltano-s3-dbt-snowflake-observability-ci-cd/
├── ingestion/                          # Meltano data ingestion pipeline
│   ├── meltano.yml                     # Meltano configuration
│   ├── observability/                  # Data quality and schema validation scripts
│   └── README.md                       # Detailed ingestion documentation
├── github_actions_ci_cd/               # CI/CD workflows and documentation
│   └── README.md                       # GitHub Actions setup guide
├── my_dbt_project/                     # dbt project for data transformation
│   ├── models/                         # dbt models (bronze, silver, gold layers)
│   ├── macros/                         # Custom dbt macros
│   ├── dbt_project.yml                 # dbt project configuration
│   └── README.md                       # dbt setup and usage guide
├── setup_env_and_s3/                   # Environment setup scripts
├── img/                                # Project images and diagrams
├── requirements-*.txt                   # Python dependencies for different components
└── README.md                           # This file
```

## ✅ Current Progress

### 🎉 **COMPLETED** - Data Ingestion Pipeline
- ✅ **Meltano Project Setup** - Configured with tap-stripe extractor and target-s3-csv loader
- ✅ **Stripe Integration** - Successfully extracting data from multiple Stripe endpoints:
  - Charges, Events, Customers, Payment Intents, Balance Transactions
- ✅ **S3 Integration** - Automatic data loading to S3 with proper folder structure
- ✅ **Data Validation** - Schema validation and data quality checks implemented
- ✅ **Documentation** - Comprehensive setup and usage guides

### 🎉 **COMPLETED** - CI/CD Pipeline
- ✅ **GitHub Actions Workflows** - Automated ingestion and observability
- ✅ **Observability Workflow** - Validates S3 files and schema compliance
- ✅ **Meltano Ingestion Workflow** - Scheduled daily data ingestion
- ✅ **Automated Testing** - Schema drift detection and file existence validation

### 🚧 **IN PROGRESS** - Data Transformation
- 🔄 **dbt Project Setup** - Basic structure configured
- 🔄 **Snowflake Integration** - Storage integration and external stage setup
- 🔄 **External Tables** - Bronze layer external tables configuration
- ⏳ **Transformation Models** - Silver and Gold layer models (pending)

### 📋 **PLANNED** - Observability & Monitoring
- ⏳ **dbt Testing** - Data quality tests and assertions
- ⏳ **Data Lineage** - Track data flow from source to consumption
- ⏳ **Performance Monitoring** - Pipeline execution metrics
- ⏳ **Alerting** - Automated notifications for data quality issues

## 🚀 Setup Instructions

### Prerequisites

Make sure you have the following installed on your local development environment:

* [Cursor AI](https://cursor.com/downloads)
  * Install `GitLens — Git supercharged` extension.
* [.venv - Virtual Environment](https://docs.python.org/3/library/venv.html)
  * cd your_repo_folder:
    * `cd "C:\PATH_TO_YOUR_REPO_FOLDER"`
  * `python -m venv .venv`           (This will create a virtual environment for the repo folder)
  * `source .venv/Scripts/activate`  (This will activate your virtual environment)
  * Install everything you need for your project from the `requirements.txt` file:
    * make sure to update pip, this is important to avoid conflicts: `python.exe -m pip install --upgrade pip`
    * `pip install --no-cache-dir -r requirements.txt`  (This will install things inside your virtual environment)
    * Check: `pip list`

* [dbt - profiles.yml - DBT_PROFILES_DIR - Connections](https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles#advanced-customizing-a-profile-directory)
  * When you invoke dbt from the command line (or from any terminal), dbt parses the `dbt_project.yml` file and obtains the 'profile name', which is where the connection credentials (the ones used to connect to your Data Warehouse) are defined. This 'profile name' is a parameter in the `dbt_project.yml` that makes reference for the any of the 'profiles' you created in the `profiles.yml` file.  
  * In order for dbt to test if the connections to databases are working, it needs to find the `profiles.yml`, which is usually located in `~/.dbt` folder.
  * However, since we have multiple dbt project, it is better to put the `profiles.yml` file within a `.dbt` folder closer to our dbt projects so that it can be easier to manage.
  * Create a `DBT_PROFILES_DIR` environment variable in Windows:
    * Windows Flag on your Keyboard + R:
      * sysdm.cpl -> Advanced Tab -> Environment Variables
      * Create a `DBT_PROFILES_DIR` variable in the "User variables for YOUR_USER" part, and put the path to your `.dbt` folder from your repo folder.
        * Example: Set `DBT_PROFILES_DIR` to C:\Projeto_dbt
    * Close and Open your VSCode
    * Go the the Git Bash Terminal (or Powershell)
    * Check it by doing: echo $DBT_PROFILES_DIR
    * Go to your dbt project folder in your repo (C:\PATH_TO_DBT_FOLDER)
    * Do: dbt debug

Make sure to include a .gitignore file with the following information:

* .venv/         (to ignore the virtual environment stuff)
* *.pyc          (to ignore python bytecode files)
* .env           (to ignore sensitive information, such as database credentials)

### Environment Variables

The .gitignore file ignores the `.env` file for security reasons. However, since this is just for educational purposes, follow the step below to include it in your project. If you do not include it, the docker will not work.

Create a `.env` file in the project root with the following content:

```bash
# S3 Configuration
S3_REGION=YOUR_REGION
S3_BUCKET_NAME=YOUR_BUCKET_NAME                            
S3_SNOWFLAKE_STORAGE_INTEGRATION=MY_S3_INTEGRATION
S3_SNOWFLAKE_STAGE=MY_S3_STAGE
S3_SNOWFLAKE_FILE_FORMAT=MY_PARQUET_FORMAT
S3_SNOWFLAKE_IAM_ROLE_ARN=arn:aws:iam::YOUR_ROLE:role/mysnowflakerole

# Snowflake Configuration
SNOWFLAKE_HOST=YOUR_HOST.YOUR_REGION.aws.snowflakecomputing.com
SNOWFLAKE_PORT=443 
SNOWFLAKE_USER=YOUR_USER
SNOWFLAKE_ROLE=STORAGE_ADMIN
SNOWFLAKE_PASSWORD=YOUR_PASSWORD
SNOWFLAKE_DBT_USER=DBT_USER
SNOWFLAKE_DBT_ROLE=DBT_ROLE
SNOWFLAKE_ACCOUNT=YOUR_ACCOUNT
SNOWFLAKE_ACCOUNT_URL=https://YOUR_HOST.YOUR_REGION.aws.snowflakecomputing.com
SNOWFLAKE_WAREHOUSE=MY_DBT_WAREHOUSE
SNOWFLAKE_DATABASE=MY_DBT_DATABASE
SNOWFLAKE_SCHEMA_BRONZE=bronze

# Stripe Configuration
STRIPE_SECRET_KEY=YOUR_STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=YOUR_STRIPE_PUBLISHABLE_KEY
```

If you want to check the environment variables from your current folder, do:
* printenv (this will show if the environmental variables were loaded within the Docker container)
* printenv | grep SNOWFLAKE (this functions as a filter to show only the variables that contain 'SNOWFLAKE')

#### Environment Variables Setup for Cursor AI

When working with Cursor AI, you may need to manually load environment variables from the `.env` file since Cursor AI starts in a fresh shell environment.

**⚠️ Important:** Always use `source` instead of `./` to load environment variables into your current shell session.

**Recommended Method (Using the Setup Script):**
```bash
source setup_env.sh
```

**Alternative Quick Setup (One-liner):**
```bash
export $(cat .env | xargs)
```

**❌ Don't use this (variables won't persist in your shell):**
```bash
./setup_env.sh
```

**Verify Environment Variables:**
```bash
printenv | grep STRIPE_SECRET_KEY
printenv | grep -E "(SNOWFLAKE|S3_)" | head -5
```

**Why use `source`?**
- `./setup_env.sh` runs the script in a subshell, so variables are not available in your current session
- `source setup_env.sh` runs the script in your current shell, making variables available for the entire session
- After running `source setup_env.sh`, all your environment variables from the `.env` file will be available in your current shell session

### AWS CLI Setup

The AWS CLI needs to be configured with credentials to interact with AWS services like S3. This setup creates a default profile using the credentials from your `.env` file.

**Prerequisites:**
- AWS CLI installed on your system
- AWS credentials configured in your `.env` file (S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_REGION)

**Setup Steps:**

1. **Configure AWS CLI with default profile:**
   ```bash
   # Set AWS Access Key ID
   aws configure set aws_access_key_id YOUR_ACCESS_KEY_ID --profile default
   
   # Set AWS Secret Access Key
   aws configure set aws_secret_access_key YOUR_SECRET_ACCESS_KEY --profile default
   
   # Set AWS Region
   aws configure set region YOUR_REGION --profile default
   
   # Set output format
   aws configure set output json --profile default
   ```

2. **Verify configuration:**
   ```bash
   aws configure list
   ```

3. **Test AWS CLI access:**
   ```bash
   # Test with your specific S3 bucket (replace with your bucket name)
   aws s3 ls s3://YOUR_BUCKET_NAME
   ```

**Troubleshooting:**

- **"Unable to locate credentials" error**: This means AWS CLI can't find credentials. Run the setup steps above.
- **"AccessDenied" error when running `aws s3 ls`**: This is a permissions issue, not a credentials issue. The user doesn't have permission to list all buckets, but can access specific buckets.
- **Multiple profiles**: If you have multiple AWS profiles, you can switch between them using `--profile profile_name` flag.

**Example with your project credentials:**
```bash
# Configure AWS CLI using environment variables
aws configure set aws_access_key_id $S3_ACCESS_KEY_ID --profile default
aws configure set aws_secret_access_key $S3_SECRET_ACCESS_KEY --profile default
aws configure set region $S3_REGION --profile default
aws configure set output json --profile default

# Test access
aws s3 ls s3://s3-observability-project
```

### Initiate the Environment

1. **Clone the repository:**

   ```bash
   git clone YOUR_GIT_REPO_URL.git
   cd "C:\PATH_TO_YOUR_REPO_FOLDER"

2. **Activate you Virtual Environment (.venv)**

* cd "C:\PATH_TO_DBT_FOLDER"
* source .venv/Scripts/activate

## 🔄 Data Ingestion Pipeline

The data ingestion pipeline is **fully operational** and extracts data from Stripe to S3 using Meltano.

### Quick Start
```bash
# Navigate to ingestion directory
cd ingestion

# Activate virtual environment
source ../.venv/Scripts/activate

# Run complete pipeline (extract from Stripe → load to S3)
meltano run tap-stripe target-s3-csv
```

### What It Does
- **Extracts** data from Stripe API (payments, customers, events, etc.)
- **Loads** data directly to S3 as timestamped CSV files
- **Validates** data quality and schema compliance
- **Automates** daily ingestion via GitHub Actions

### Data Sources
- **Stripe Endpoints**: charges, events, customers, payment_intents, balance_transactions
- **Output Format**: CSV files with automatic timestamping
- **Storage**: S3 with organized folder structure (`raw/stripe/`)

For detailed setup and usage instructions, see [ingestion/README.md](ingestion/README.md).

## 🚀 CI/CD Pipeline

The project includes **automated CI/CD pipelines** that ensure data quality and reliability.

### Workflows

1. **Observability Workflow (CI)**
   - Validates S3 files exist and schema matches expectations
   - Runs on every push to main branch
   - Ensures data quality and detects schema drift

2. **Meltano Ingestion Workflow (CD)**
   - Automates daily Stripe data ingestion
   - Scheduled daily at 23:00 Europe/Madrid
   - Ensures consistent data pipeline execution

### Key Features
- **Automated Testing**: Schema validation and file existence checks
- **Scheduled Ingestion**: Daily data pipeline execution
- **Quality Gates**: Fail-fast on data quality issues
- **Manual Triggers**: On-demand pipeline execution

For detailed CI/CD setup, see [github_actions_ci_cd/README.md](github_actions_ci_cd/README.md).

## 🔄 Data Transformation (dbt + Snowflake)

The data transformation layer is **partially implemented** and ready for completion.

### Current Status
- ✅ **dbt Project Structure**: Bronze, Silver, Gold layer architecture
- ✅ **Snowflake Integration**: Storage integration and external stage setup
- ✅ **External Tables**: Bronze layer external tables configuration
- 🔄 **Transformation Models**: Silver and Gold layer models (in progress)

### Architecture
- **Bronze Layer**: Raw data from S3 as external tables
- **Silver Layer**: Cleaned and standardized data models
- **Gold Layer**: Aggregated business metrics and KPIs

### Next Steps for dbt
1. **Complete External Tables Setup**
   ```bash
   cd my_dbt_project
   dbt run-operation stage_external_sources
   ```

2. **Build Transformation Models**
   ```bash
   dbt run
   ```

3. **Implement Data Quality Tests**
   ```bash
   dbt test
   ```

For detailed dbt setup, see [my_dbt_project/README.md](my_dbt_project/README.md).

## 🎯 Next Steps

### Immediate Priorities
1. **Complete dbt Models**
   - Finish Silver layer transformation models
   - Implement Gold layer aggregation models
   - Add comprehensive data quality tests

2. **Enhanced Observability**
   - Implement dbt testing framework
   - Add data lineage tracking
   - Set up performance monitoring

3. **Production Readiness**
   - Add error handling and retry logic
   - Implement comprehensive logging
   - Set up alerting and notifications

### Future Enhancements
- **Real-time Processing**: Stream processing with Kafka/Spark
- **Advanced Analytics**: ML model integration and predictions
- **Multi-source Ingestion**: Additional data sources beyond Stripe
- **Data Governance**: Data catalog and metadata management

## 📚 Resources

- [Meltano Documentation](https://docs.meltano.com/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🤝 Contributing

This project demonstrates modern data engineering best practices. Feel free to:
- Report issues or bugs
- Suggest improvements
- Contribute additional features
- Share your own implementations

---

**Project Status**: 🟡 **Phase 2 of 4 Complete** - Data ingestion and CI/CD operational, transformation layer in progress