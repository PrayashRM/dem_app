#!/bin/sh

set -e

echo "──────────────────────────────────────────"
echo " Starting Product Management System"
echo "──────────────────────────────────────────"

echo "[1/3] Waiting for PostgreSQL to be ready..."

# Wait until Postgres is accepting connections
until python -c "
import psycopg2, os, sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'  DB not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
  echo "  PostgreSQL is not ready yet. Retrying in 2 seconds..."
  sleep 2
done

echo "  PostgreSQL is ready."

echo "[2/3] Running Alembic database migrations..."
alembic upgrade head
echo "  Migrations applied."

echo "[3/3] Running seed script..."
python scripts/seed.py
echo "  Seed complete."

echo "──────────────────────────────────────────"
echo " Starting FastAPI application..."
echo "──────────────────────────────────────────"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    --no-access-log