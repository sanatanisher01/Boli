#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install psycopg adapter first
pip install --no-cache-dir psycopg[binary]==3.1.18

# Install requirements with no cache to avoid conflicts
pip install --no-cache-dir -r requirements.txt

# Skip collectstatic if running locally
if [ "$RENDER" == "true" ]; then
  # Collect static files
  python manage.py collectstatic --no-input
  
  # Run migrations
  python manage.py migrate
fi