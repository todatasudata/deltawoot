#!/bin/bash

sudo docker login

COMMIT_HASH=$(git rev-parse --short HEAD)

IMAGE_NAME="todatasudata/deltawoot"

sudo docker tag deltawoot $IMAGE_NAME:$COMMIT_HASH

sudo docker push $IMAGE_NAME:$COMMIT_HASH

sudo docker tag deltawoot $IMAGE_NAME:latest
sudo docker push $IMAGE_NAME:latest


echo "Docker image tagged and pushed with commit hash: $COMMIT_HASH"

