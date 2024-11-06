#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting IVAN services..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Please run ./scripts/docker/build.sh first"
    exit 1
fi

# Start services
echo "📦 Starting Docker containers..."
docker compose up -d

echo "🔍 Checking service health..."
sleep 5

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo "📝 Logs can be viewed with: docker compose logs -f"
else
    echo "❌ Some services failed to start. Check logs with: docker compose logs"
    exit 1
fi 