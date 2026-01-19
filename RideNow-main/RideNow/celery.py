import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RideNow.settings')

app = Celery('RideNow')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule configuration
app.conf.beat_schedule = {
    'send-periodic-email-reports': {
        'task': 'core.tasks.send_periodic_email_reports',
        'schedule': 60.0 * 60 * 24,  # Run daily
    },
    'cleanup-expired-sessions': {
        'task': 'core.tasks.cleanup_expired_sessions',
        'schedule': 60.0 * 60 * 6,  # Run every 6 hours
    },
    'update-driver-scores': {
        'task': 'rides.tasks.update_driver_scores',
        'schedule': 60.0 * 60 * 12,  # Run every 12 hours
    },
}

app.conf.timezone = 'Africa/Kampala'

# Optional configuration for better performance and monitoring
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Kampala',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
