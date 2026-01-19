from django.core.management.base import BaseCommand
from celery import current_app
import redis


class Command(BaseCommand):
    help = 'Check Celery worker and Redis status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking Celery status...'))
        
        # Check Redis connection
        try:
            r = redis.Redis(host='127.0.0.1', port=6379, db=0)
            r.ping()
            self.stdout.write(self.style.SUCCESS('✓ Redis connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Redis connection: FAILED - {e}'))
            return
        
        # Check Celery workers
        try:
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                self.stdout.write(self.style.SUCCESS('✓ Celery workers: ACTIVE'))
                for worker, stat in stats.items():
                    self.stdout.write(f'  - {worker}: {stat.get("total", 0)} tasks processed')
            else:
                self.stdout.write(self.style.WARNING('⚠ Celery workers: NO ACTIVE WORKERS'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Celery workers: FAILED - {e}'))
        
        # Check registered tasks
        try:
            inspect = current_app.control.inspect()
            registered = inspect.registered()
            
            if registered:
                self.stdout.write(self.style.SUCCESS('✓ Registered tasks:'))
                for worker, tasks in registered.items():
                    self.stdout.write(f'  - {worker}: {len(tasks)} tasks')
                    for task in tasks[:5]:  # Show first 5 tasks
                        self.stdout.write(f'    * {task}')
                    if len(tasks) > 5:
                        self.stdout.write(f'    ... and {len(tasks) - 5} more')
            else:
                self.stdout.write(self.style.WARNING('⚠ No registered tasks found'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Task registration: FAILED - {e}'))
        
        self.stdout.write(self.style.SUCCESS('\nCelery status check completed!'))
