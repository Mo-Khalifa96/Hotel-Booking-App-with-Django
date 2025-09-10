#!/bin/bash
set -euo pipefail

#Set DJANGO_SETTINGS_MODULE as production settings (works for the duration of the script's execution only!)
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-HotelBookingProject.settings.prod}

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting files..."
python manage.py collectstatic --noinput


#Gunicorn socket directory
mkdir -p /run/gunicorn


#Identify number of CPU cores on system
CPU_CORES=$(nproc --all)

#Rule of thumb: (2 * cores) + 1
WORKERS=$(( 2 * CPU_CORES + 1 ))


#Start Gunicorn server
echo "Starting Gunicorn (prod) on unix socket..."
exec gunicorn HotelBookingProject.wsgi:application \
  --bind "unix:/run/gunicorn/gunicorn.sock" \
  --workers "$WORKERS" \
  --timeout 60 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile - \
  --log-level info

