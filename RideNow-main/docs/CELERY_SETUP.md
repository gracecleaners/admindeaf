# Celery Configuration for RideNow

This document explains how to set up and run Celery for the RideNow application.

## Prerequisites

1. **Redis Server**: Celery uses Redis as the message broker
2. **Python Dependencies**: Already included in requirements.txt
   - `celery==5.4.0`
   - `redis==6.4.0`
   - `django-celery-beat==2.7.0`

## Installation

### 1. Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 2. Database Migrations

Run migrations to create Celery Beat tables:

```bash
python manage.py migrate
```

## Configuration

### Celery Configuration Files

- `RideNow/celery.py` - Main Celery configuration
- `RideNow/__init__.py` - Celery app initialization
- `RideNow/settings.py` - Django settings with Celery config

### Key Settings

```python
# Development and Production
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TIMEZONE = 'Africa/Kampala'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

## Running Celery

### Development

```bash
# Start all Celery services
./start_celery_dev.sh

# Or start individually:
# Worker
celery -A RideNow worker --loglevel=debug --concurrency=2 --reload

# Beat (periodic tasks)
celery -A RideNow beat --loglevel=debug --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Flower (monitoring)
celery -A RideNow flower --port=5555
```

### Production

```bash
# Start all services
./start_celery.sh

# Or use Supervisor (recommended)
sudo cp dev_ops/celery_supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
sudo supervisorctl start celery_flower
```

## Available Tasks

### Core Tasks (`core/tasks.py`)

- `create_profile(user_id)` - Create user profile
- `send_sms_alert_task(body, sms_phone)` - Send SMS alerts
- `send_email_task(email, subject, message, is_html=False)` - Send emails
- `send_periodic_email_reports()` - Daily admin reports
- `cleanup_expired_sessions()` - Clean old sessions

### Rides Tasks (`rides/tasks.py`)

- `update_driver_scores()` - Update driver performance scores
- `cleanup_old_rides()` - Clean up old completed rides
- `send_ride_reminders()` - Send ride reminders

## Periodic Tasks (Celery Beat)

Configured in `RideNow/celery.py`:

- **Daily Email Reports**: Every 24 hours
- **Session Cleanup**: Every 6 hours
- **Driver Score Updates**: Every 12 hours

## Monitoring

### Flower (Web Interface)

Access at: http://localhost:5555

Features:
- Task monitoring
- Worker status
- Task history
- Real-time statistics

### Management Commands

```bash
# Check Celery status
python manage.py celery_status

# List registered tasks
celery -A RideNow inspect registered

# Check active workers
celery -A RideNow inspect active

# Check scheduled tasks
celery -A RideNow inspect scheduled
```

## Usage Examples

### Calling Tasks from Django Views

```python
from core.tasks import send_email_task, send_sms_alert_task

# Send email asynchronously
send_email_task.delay(
    email='user@example.com',
    subject='Welcome to RideNow',
    message='Thank you for joining!',
    is_html=False
)

# Send SMS asynchronously
send_sms_alert_task.delay(
    body='Your ride is confirmed!',
    sms_phone='+256700000000'
)
```

### Scheduling Tasks

```python
from datetime import datetime, timedelta
from core.tasks import send_email_task

# Schedule task for later
eta = datetime.now() + timedelta(hours=1)
send_email_task.apply_async(
    args=['user@example.com', 'Subject', 'Message'],
    eta=eta
)
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   redis-cli ping
   
   # Start Redis if not running
   sudo systemctl start redis-server
   ```

2. **Worker Not Starting**
   ```bash
   # Check for import errors
   python manage.py shell
   >>> from core.tasks import send_email_task
   
   # Check Celery status
   python manage.py celery_status
   ```

3. **Tasks Not Executing**
   ```bash
   # Check worker logs
   tail -f /var/log/celery/worker.log
   
   # Check if tasks are registered
   celery -A RideNow inspect registered
   ```

### Log Files

- Worker logs: `/var/log/celery/worker.log`
- Beat logs: `/var/log/celery/beat.log`
- Flower logs: `/var/log/celery/flower.log`

## Production Considerations

1. **Use Supervisor**: For process management and auto-restart
2. **Monitor Resources**: Set appropriate concurrency levels
3. **Log Rotation**: Configure logrotate for Celery logs
4. **Redis Persistence**: Configure Redis for data persistence
5. **Security**: Use authentication for Flower in production

## Performance Tuning

### Worker Configuration

```python
# In settings.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
```

### Redis Configuration

```bash
# In /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Security

1. **Redis Security**: Set password for Redis in production
2. **Network Security**: Restrict Redis access to localhost
3. **Flower Security**: Use authentication for Flower web interface
4. **Task Security**: Validate task inputs and use proper error handling
