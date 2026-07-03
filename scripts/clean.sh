#!/usr/bin/env bash
set -euo pipefail
echo "Stopping and removing containers, networks and volumes..."
docker-compose down -v --remove-orphans
echo "Cleaned."
