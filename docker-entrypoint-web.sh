#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Compile translation messages
echo "Compiling messages..."
python manage.py compilemessages || echo "No new messages to compile or compilemessages failed"

# Start Gunicorn by executing the command passed to the script
echo "Starting Gunicorn..."
exec "$@"
