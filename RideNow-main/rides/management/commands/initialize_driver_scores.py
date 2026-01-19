#!/usr/bin/env python
"""
Management command to initialize driver scores for existing drivers
"""
from django.core.management.base import BaseCommand
from accounts.models import DriverProfile
from rides.models import DriverScore


class Command(BaseCommand):
    help = 'Initialize driver scores for existing drivers'

    def handle(self, *args, **options):
        self.stdout.write('Initializing driver scores...')
        
        created_count = 0
        updated_count = 0
        
        for driver in DriverProfile.objects.all():
            driver_score, created = DriverScore.objects.get_or_create(
                driver=driver,
                defaults={
                    'acceptance_rate': 100.0,
                    'response_time_avg': 30.0,  # Default 30 seconds
                    'cancellation_rate': 0.0,
                    'completion_rate': 100.0,
                    'reliability_score': 100.0,
                    'availability_score': 100.0,
                    'total_requests': 0,
                    'accepted_requests': 0,
                    'declined_requests': 0,
                    'timeout_requests': 0,
                    'cancelled_rides': 0,
                    'completed_rides': 0
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created score for driver: {driver.username}')
            else:
                updated_count += 1
                # Update scores based on existing data
                driver_score.update_scores()
                self.stdout.write(f'Updated score for driver: {driver.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} drivers. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )

