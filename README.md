# Later....

<img src = ""> 

## Table of Contents

- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Initiate the Environment](#initiate-the-environment)
- [dbt](#dbt)

## Project Structure

- **observability_project (project-root)/**
    - **.venv/**
    - **my_dbt_project/**   (This is where your dbt project lives)
    - **img/**
    - **.env**
    - **.gitignore**
    - **requirements.txt**
    - **README.md**

## Setup Instructions

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

Make sure to inclue a .gitignore file with the following information:

* .venv/         (to ignore the virtual environment stuff)
* *.pyc          (to ignore python bytecode files)
* .env           (to ignore sensitive information, such as database credentials)

### Environment Variables
The .gitignore file, ignores the `.env` file for security reasons. However, since this is just for educational purposes, follow the step below to include it in your project. If you do not include it, the docker will not work.

Create a `.env` file in the project root with the following content:

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
   cd "C:\PATH_TO_DBT_FOLDER"

2. **Activate you Virtual Environment (.venv)**

* cd "C:\PATH_TO_DBT_FOLDER"
* source .venv/Scripts/activate

## dbt

* Go to the `dbt_transformation/` folder and operate dbt by following the `README` in there.
  * cd "C:\PATH_TO_DBT_FOLDER"
  * `dbt debug`