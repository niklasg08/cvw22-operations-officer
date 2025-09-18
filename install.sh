#!/bin/bash

echo "Starting installation..."
echo "Creating environment file..."

read -p "Enter your bot token: " BOT_TOKEN
read -p "Enter your Brevity Term channel ID: " DISCORD_CHANNEL_BREVITY
read -p "Enter your Recap channel ID: " DISCORD_CHANNEL_RECAP

if [ ! -d "src/bot/.env" ]; then
    touch src/bot/.env
fi

echo "DISCORD_TOKEN=${BOT_TOKEN}" > src/bot/.env
echo "DISCORD_CHANNEL_BREVITY=${DISCORD_CHANNEL_BREVITY}" >> src/bot/.env
echo "DISCORD_CHANNEL_RECAP=${DISCORD_CHANNEL_RECAP}" >> src/bot/.env

echo "Creating virtual environment..."
cd ./src/bot
python3 -m venv .venv
source .venv/bin/activate

echo "Setting up virtual environment..."
pip install --upgrade pip
pip install -r ../../requirements.txt

echo "Installation complete."
