#!/bin/bash

# Start Celery Worker
echo "Starting Celery Worker..."
celery -A RideNow worker --loglevel=info --concurrency=4 &

# Start Celery Beat (for periodic tasks)
echo "Starting Celery Beat..."
celery -A RideNow beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Start Celery Flower (for monitoring - optional)
echo "Starting Celery Flower (monitoring)..."
celery -A RideNow flower --port=5555 &

echo "Celery services started!"
echo "Worker: Running in background"
echo "Beat: Running in background" 
echo "Flower: http://localhost:5555"
echo ""
echo "To stop all services, run: pkill -f celery"
