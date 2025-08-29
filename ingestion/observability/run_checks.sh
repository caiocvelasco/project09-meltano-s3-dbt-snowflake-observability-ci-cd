#!/bin/bash

echo "Running S3 file check..."
python 01_check_s3_files.py
FILES_OK=$?

echo "Running S3 schema check..."
python 02_check_s3_schema.py
SCHEMA_OK=$?

if [ $FILES_OK -eq 0 ] && [ $SCHEMA_OK -eq 0 ]; then
    echo "All S3 ingestion checks passed!"
    exit 0
else
    echo "Some S3 ingestion checks failed!"
    exit 1
fi
