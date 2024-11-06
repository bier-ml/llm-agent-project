#!/bin/bash

# Make docker scripts executable
chmod +x scripts/docker/build.sh
chmod +x scripts/docker/up.sh
chmod +x scripts/docker/down.sh

# Make setup scripts executable
chmod +x scripts/setup/make_executable.sh

echo "✅ All scripts are now executable!" 