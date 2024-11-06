# IVAN Scripts

This directory contains various scripts for managing the IVAN project.

## Directory Structure

- `docker/` - Scripts for Docker operations
  - `build.sh` - Build Docker images
  - `up.sh` - Start Docker services
  - `down.sh` - Stop Docker services

- `setup/` - Setup and installation scripts
  - `make_executable.sh` - Make all scripts executable
  - `install_dependencies.sh` - Install project dependencies

## Usage

1. First time setup:
```bash
chmod +x scripts/setup/make_executable.sh
./scripts/setup/make_executable.sh
```

2. Docker operations:
```bash
./scripts/docker/build.sh  # Build services
./scripts/docker/up.sh     # Start services
./scripts/docker/down.sh   # Stop services
```

3. Install dependencies (for local development):
```bash
./scripts/setup/install_dependencies.sh
``` 