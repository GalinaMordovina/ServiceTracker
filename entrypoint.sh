#!/usr/bin/env sh
set -e

echo "==> Waiting for database..."

python - <<'PY'
import os
import time
import socket

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

deadline = time.time() + 60
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("==> DB port is open")
            break
    except OSError:
        if time.time() > deadline:
            raise SystemExit("DB is not available after 60 seconds")
        print("... still waiting for DB")
        time.sleep(2)
PY

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Starting gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
