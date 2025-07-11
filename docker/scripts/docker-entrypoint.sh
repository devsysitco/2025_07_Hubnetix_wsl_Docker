#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
until mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASSWORD}" -e "SELECT 1" > /dev/null 2>&1; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Database is ready!"

# Run Django management commands
echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create media directory if it doesn't exist
mkdir -p /var/lib/django/media

# Set proper permissions
chown -R django:django /var/lib/django/static /var/lib/django/media

echo "Starting application..."
exec "$@"
