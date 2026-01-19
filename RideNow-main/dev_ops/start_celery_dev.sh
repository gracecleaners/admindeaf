#!/bin/bash

# Development Celery startup script
echo "Starting Celery for Development..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start Celery Worker with auto-reload
echo "Starting Celery Worker (development mode)..."
celery -A RideNow worker --loglevel=debug --concurrency=2 --reload &

# Start Celery Beat
echo "Starting Celery Beat..."
celery -A RideNow beat --loglevel=debug --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo ""
echo "Development Celery services started!"
echo "Worker: Running with auto-reload"
echo "Beat: Running for periodic tasks"
echo ""
echo "To stop: ./stop_celery.sh"
echo "To view logs: tail -f /var/log/celery.log"
