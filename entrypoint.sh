#!/bin/bash

# Check if SERVICE_ACCOUNT_JSON is provided
if [ -z "$SERVICE_ACCOUNT_JSON" ]; then
  echo "Error: SERVICE_ACCOUNT_JSON is not provided"
  exit 1
fi

# Check if PROJECT_ID is provided
if [ -z "$GCP_PROJECT_ID" ]; then
  echo "Error: GCP_PROJECT_ID is not provided"
  exit 1
fi

# Start the Docker daemon
service docker start

# Check if the Docker daemon is running
timeout 20 sh -c 'until docker info; do echo "Waiting for Docker to start..."; sleep 1; done'

# Decode and write the JSON to a temporary file
echo "$SERVICE_ACCOUNT_JSON" > /tmp/service_account_key.json

# Activate the service account with gcloud
gcloud auth activate-service-account --key-file=/tmp/service_account_key.json --quiet

# Set the Google Cloud project
gcloud config set project $GCP_PROJECT_ID --quiet

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Run the main command
python3 -m com.mhire.startup_fine_tuning
