#!/bin/bash

# Get parent directory of this script
APPLICATION_DIR=$(dirname "$(readlink -f "$0")")

# Move to the application directory
cd "$APPLICATION_DIR" || exit 1

# Image name
IMAGE_NAME="ghcr.io/dataforgoodfr/us_climate_data_dispatcher"

# Build docker image
docker build -t $IMAGE_NAME:latest .

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed."
    exit 1
else
    echo "Docker build succeeded."

    # Push the image to GitHub Container Registry
    docker push $IMAGE_NAME --all-tags
fi