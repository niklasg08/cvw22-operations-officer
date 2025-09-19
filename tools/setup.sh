#!/bin/bash

echo "Starting setup..."

cd ~/cvw22-operations-officer

echo "Checking if environment file exists..."
if [ ! -f "src/bot/.env" ]; then
    echo "Environment file not found! Please run the install script first."
    exit 1
fi

echo "Creating data directory..."
sudo mkdir -p /opt/docker/volumes/cvw22-operations-officer/data

echo "Copying data files to opt directory..."
sudo cp -r src/bot/data /opt/docker/volumes/cvw22-operations-officer

echo "Setting permissions..."
sudo chmod 776 /opt/docker/volumes/cvw22-operations-officer/data/brevityTerms.csv
sudo chmod 776 /opt/docker/volumes/cvw22-operations-officer/data/data.json

echo "Creating log directory..."
sudo mkdir -p /opt/docker/logs/cvw22-operations-officer

echo "Setting permissions..."
sudo chmod 776 /opt/docker/logs/cvw22-operations-officer

echo "Setup complete!"
