#!/bin/bash

# Exit on error
set -o errexit

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start gunicorn
echo "Starting Gunicorn..."
exec gunicorn realtor_pal.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile -
