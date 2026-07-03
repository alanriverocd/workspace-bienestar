#!/usr/bin/env bash
set -euo pipefail
echo "Running DB seed inside control_backend container..."
docker-compose exec -T control_backend bash -lc "python - <<'PY'
import asyncio
from app.seed_data import create_sample
asyncio.run(create_sample())
PY"
echo "Seed finished."
