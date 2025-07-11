# Use Ubuntu as base image, matching Odoo setup
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables for Python and Django
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    VIRTUAL_ENV=/opt/django/venv \
    PATH="/opt/django/venv/bin:$PATH"

# Create django user with specific UID/GID for permission management
RUN groupadd -g 1000 django && \
    useradd -u 1000 -g django -d /opt/django -m -s /bin/bash django

# Install system dependencies including MySQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-wheel \
    python3-setuptools \
    libmysqlclient-dev \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    mysql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Set up directories with proper permissions
RUN mkdir -p /var/lib/django/static \
    /var/lib/django/media \
    /var/log/django \
    && chown -R django:django /var/lib/django /var/log/django

# Switch to django user
USER django

# Create and activate virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Set working directory
WORKDIR /opt/django/django_project

# Copy requirements first for better cache utilization
COPY --chown=django:django requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY --chown=django:django . .

# Expose port for Gunicorn
EXPOSE 8001

# Add startup script
COPY --chown=django:django docker/scripts/docker-entrypoint.sh /opt/django/
RUN chmod +x /opt/django/docker-entrypoint.sh

# Entrypoint and default command
ENTRYPOINT ["/opt/django/docker-entrypoint.sh"]
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8001", "photoproject.wsgi:application"]
