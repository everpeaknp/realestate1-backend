#!/bin/bash

# Exit on error
set -o errexit

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

if [ "${PROPERTY_FEED_SOURCE:-EAGLE_API}" = "REAXML" ] && [ "${REAXML_IMPORT_ON_START:-false}" = "true" ]; then
  echo "Importing REAXML feed..."
  if [ -n "${REAXML_LOCAL_DIR:-}" ]; then
    python manage.py import_reaxml_feed --local-dir "$REAXML_LOCAL_DIR" || true
  else
    python manage.py import_reaxml_feed --from-ftp || true
  fi
fi

# Start gunicorn
echo "Starting Gunicorn..."
exec gunicorn realtor_pal.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile -
