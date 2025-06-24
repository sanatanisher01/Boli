#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install PostgreSQL adapter first
pip install --no-cache-dir psycopg[binary]==3.2.9

# Install requirements with no cache to avoid conflicts
pip install --no-cache-dir -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate