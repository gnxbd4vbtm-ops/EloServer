#!/bin/bash
# Production server startup script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Set production environment
export DEBUG=False
export ALLOWED_HOSTS="127.0.0.1,localhost"

# Run migrations (if needed)
python manage.py makemigrations
python manage.py migrate

# Start gunicorn ASGI server with 4 workers and Uvicorn worker class
gunicorn --workers 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --log-level info elosystem.asgi:application
