#!/bin/bash
set -e

# Create logging directory
mkdir -p /var/log/django
touch /var/log/django/django.log

# Wait for MySQL to be ready
wait_for_mysql() {
    local retries=30
    echo "Waiting for MySQL to be ready..."
    
    while [ $retries -gt 0 ]; do
        if mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent 2>/dev/null; then
            echo "MySQL is ready!"
            return 0
        fi
        
        retries=$((retries - 1))
        echo "Waiting for MySQL to be ready... ($retries attempts left)"
        sleep 2
    done
    
    echo "Failed to connect to MySQL after 30 attempts. Exiting."
    exit 1
}

# Set environment variables for MySQL (use defaults if not set)
DB_HOST=${DB_HOST:-db}
DB_USER=${DB_USER:-admin}
DB_PASSWORD=${DB_PASSWORD:-Django@Secure2024!}

# Wait for MySQL
wait_for_mysql

echo "Running Django migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django application..."
exec "$@"
