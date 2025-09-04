#!/bin/bash

# Start running startup script
echo "Start running startup script..."

#Image name to pull from artifact registry
image_name="mistral-image"

#Tag for the image being pulled 
tag_name="v1.0"

# Pull the latest docker image from artifact registry
#docker pull [REGISTRY_URL]/[PROJECT_ID]/[REPOSITORY]/[IMAGE_NAME]:[TAG]
docker pull us-central1-docker.pkg.dev/sandbox-10fb8/fine-tuned-llm-models/$image_name:$tag_name

#name of the image 
image_name="us-central1-docker.pkg.dev/sandbox-10fb8/fine-tuned-llm-models/$image_name:$tag_name"

# Check if the container already exists
if [ $(docker ps -a -q -f name=llm-container) ]; then
  # Stop and remove the existing container
  docker stop llm-container
  docker rm llm-container
fi

# Run the llm container exposing at port 11434
docker run -d --name llm-container -p 11434:11434 $image_name

