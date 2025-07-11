#!/bin/bash
set -e

PROJECT_DIR="/home/ubuntu/django_project"
LOG_FILE="$PROJECT_DIR/pull_code.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting code pull"

# Ensure we're in the project directory
cd "$PROJECT_DIR" || { log "Failed to navigate to $PROJECT_DIR"; exit 1; }

# Start SSH agent and add the key
eval "$(ssh-agent -s)" || { log "Failed to start SSH agent"; exit 1; }
ssh-add ~/.ssh/github_actions || { log "Failed to add SSH key"; exit 1; }

log "SSH agent started and key added"

# Pull the latest code
log "Pulling latest code from Git"
git pull origin main || { log "Git pull failed"; exit 1; }

log "Code pull completed successfully"

# Kill the SSH agent
ssh-agent -k || log "Warning: Failed to kill SSH agent"
