#!/usr/bin/env bash
set -euo pipefail
# Simple helper to run bulk seed inside backend container
# Usage: ./scripts/seed-many.sh <total> [batch]
TOTAL=${1:-1000}
BATCH=${2:-100}
echo "Seeding $TOTAL records in batches of $BATCH..."
docker-compose exec -T control_backend bash -lc "python /app/seed_data.py --many ${TOTAL} --batch ${BATCH}"
echo "Done."
