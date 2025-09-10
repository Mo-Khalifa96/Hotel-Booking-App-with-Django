#!/bin/bash
set -euo pipefail

#Set DJANGO_SETTINGS_MODULE as development settings (works for the duration of the script's execution only!)
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-HotelBookingProject.settings.dev}

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting files..."
python manage.py collectstatic --noinput

#import data once after setup
if [ ! -f "/app/.seeded" ]; then
  echo "Importing initial data..."
  python manage.py import_branches --csv-file seed/branches.csv
  python manage.py import_rooms --csv-file seed/rooms.csv
  echo "Creating dummy bookings..."
  python manage.py create_dummy_bookings
  touch /app/.seeded
fi

#Identify number of CPU cores on system
CPU_CORES=$(nproc --all)

#Rule of thumb: (2 * cores) + 1
WORKERS=$(( 2 * CPU_CORES + 1 ))


#Start Gunicorn server
echo "Starting Gunicorn (dev) on 0.0.0.0:8000..."
exec gunicorn HotelBookingProject.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "$WORKERS" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --log-level info