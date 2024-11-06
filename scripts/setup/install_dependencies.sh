#!/bin/bash

# Exit on error
set -e

echo "📦 Installing project dependencies..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "🔧 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "🔨 Installing project dependencies..."
poetry install

echo "✅ Dependencies installed successfully!" 