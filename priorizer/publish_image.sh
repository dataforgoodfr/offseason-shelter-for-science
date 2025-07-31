#!/bin/bash

# Get parent directory of this script
APPLICATION_DIR=$(dirname "$(readlink -f "$0")")

# Move to the application directory
cd "$APPLICATION_DIR" || exit 1

# Image name
IMAGE_NAME="ghcr.io/dataforgoodfr/us_climate_data_priorizer"

# Build docker image
docker build -t $IMAGE_NAME:latest .

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed."
    exit 1
else
    echo "Docker build succeeded."

    # Create a personal Github token with write:packages permission
    # cf https://docs.github.com/fr/packages/working-with-a-github-packages-registry/working-with-the-container-registry
    docker login ghcr.io -u USERNAME -p $GHCR_TOKEN

    # Push the image to GitHub Container Registry
    docker push $IMAGE_NAME --all-tags
fi