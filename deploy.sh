#!/bin/bash
# Exit on any error
set -e

# Define project directory
PROJECT_DIR="/home/ubuntu/django_project"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/deployment.log"

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Start deployment
log "Starting deployment"

# Navigate to project directory
cd "$PROJECT_DIR" || { log "Failed to navigate to $PROJECT_DIR"; exit 1; }

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    log "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR" || { log "Failed to create virtual environment"; exit 1; }
fi

# Activate virtual environment
log "Activating virtual environment"
source "$VENV_DIR/bin/activate" || { log "Failed to activate virtual environment"; exit 1; }

# Upgrade pip
log "Upgrading pip"
pip install --upgrade pip || { log "Failed to upgrade pip"; exit 1; }

# Install dependencies
log "Installing dependencies"
pip install -r requirements.txt || { log "Failed to install dependencies"; exit 1; }

# Run migrations
log "Running migrations"
python manage.py makemigrations || { log "Makemigrations failed"; exit 1; }
python manage.py migrate || { log "Migrate failed"; exit 1; }

# Collect static files
log "Collecting static files"
python manage.py collectstatic --noinput || { log "Collectstatic failed"; exit 1; }

# Restart services (only if they exist)
if systemctl is-active --quiet gunicorn; then
    log "Restarting Gunicorn"
    sudo systemctl restart gunicorn || { log "Gunicorn restart failed"; exit 1; }
else
    log "Gunicorn service not found or not active"
fi

if systemctl is-active --quiet nginx; then
    log "Restarting Nginx"
    sudo systemctl restart nginx || { log "Nginx restart failed"; exit 1; }
else
    log "Nginx service not found or not active"
fi

# Deactivate virtual environment
deactivate

log "Deployment completed successfully"
