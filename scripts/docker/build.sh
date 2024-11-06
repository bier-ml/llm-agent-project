#!/bin/bash

# Exit on error
set -e

echo "🏗️ Building IVAN services..."

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️ Please update .env with your actual credentials"
fi

# Build the images
echo "🔨 Building Docker images..."
docker compose build

echo "✅ Build completed successfully!" 