#!/bin/bash

echo "Stopping Celery services..."

# Stop all celery processes
pkill -f "celery.*RideNow"

# Wait a moment for graceful shutdown
sleep 2

# Force kill if still running
pkill -9 -f "celery.*RideNow"

echo "Celery services stopped!"
