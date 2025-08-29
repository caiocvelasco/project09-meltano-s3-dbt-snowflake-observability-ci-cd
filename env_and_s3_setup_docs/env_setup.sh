#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | xargs)
    echo "Environment variables loaded successfully!"
    echo "Available variables:"
    printenv | grep -E "(SNOWFLAKE|S3_|STRIPE_)" | sort
else
    echo "Error: .env file not found!"
    exit 1
fi

