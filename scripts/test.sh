#!/usr/bin/env bash
set -euo pipefail
echo "Running backend tests with coverage..."
docker run --rm -v "$(pwd)/backend:/app" -w /app python:3.11-slim bash -lc "pip install -r requirements.txt && pytest --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=80"
echo "Frontend tests not configured; add if needed."
