#!/usr/bin/env bash
set -euo pipefail
echo "Building and starting containers..."
docker-compose build --pull
docker-compose up -d
echo "Initializing database schema..."
sleep 3
docker-compose exec -T control_backend bash -lc "alembic upgrade head || python -c \"import asyncio; from app.db import init_db; asyncio.run(init_db()); print('db ready')\""
echo "All services up. Frontend: http://localhost:5173 Backend: http://localhost:8000"
