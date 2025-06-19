#!/bin/bash

#Exit immediately if any command fails
set -e

#Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

#Collect static files
echo "Collecting static files..."
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

#Determine Gunicorn bind address based on IS_DOCKERIZED flag (set in .env file)
IS_DOCKERIZED=$(printenv IS_DOCKERIZED | tr '[:upper:]' '[:lower:]')
IS_DOCKERIZED=${IS_DOCKERIZED:-false}

GUNICORN_BIND=""
if [ "$IS_DOCKERIZED" = "true" ]; then
  #for Dockerized environments (dev or prod), bind to Unix socket for Nginx
  GUNICORN_BIND="unix:/run/gunicorn/gunicorn.sock"
else
  #for local development outside Docker, bind to a standard TCP port
  GUNICORN_BIND="0.0.0.0:8000"
fi

#Start Gunicorn server
echo "Starting Gunicorn with bind: $GUNICORN_BIND"
exec gunicorn HotelBookingProject.wsgi:application \
  --bind "$GUNICORN_BIND" \
  --workers 4 \
  --threads 2 \
  --timeout 90

