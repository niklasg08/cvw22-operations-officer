#!/bin/bash

echo "Starting update..."

cd ~/cvw22-operations-officer

echo "Getting the latest image..."
docker compose pull cvw22-operations-officer

echo "Stopping and deleting current container..."
docker stop cvw22-operations-officer
docker rm cvw22-operations-officer

echo "Starting new container with the latest image..."
docker compose up -d

echo "Update complete!"
