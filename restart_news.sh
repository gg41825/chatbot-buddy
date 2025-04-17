#!/bin/bash

# set the names of image and container
IMAGE_ALIAS="news"
CONTAINER_ALIAS="c-news"

# Step 1: build new image
echo "Building Docker image: $IMAGE_ALIAS"
docker build -t $IMAGE_ALIAS .

# Step 2: find and stop old container（if exists）
OLD_CONTAINER_ID=$(docker ps -aqf "name=$CONTAINER_ALIAS")

if [ -n "$OLD_CONTAINER_ID" ]; then
  echo "🛑 stopping container: $OLD_CONTAINER_ID"
  docker stop $OLD_CONTAINER_ID
  echo "🧹 deleting container: $OLD_CONTAINER_ID"
  docker rm $OLD_CONTAINER_ID
else
  echo "✅ no old container found"
fi

# Step 3: start new container
echo "🚀 restarting container: $CONTAINER_ALIAS"
docker container run --name $CONTAINER_ALIAS -d -p 8080:80 $IMAGE_ALIAS

echo "🎉 Done! New container is using port 8080"