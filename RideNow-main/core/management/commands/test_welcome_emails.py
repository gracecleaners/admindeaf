from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.tasks import send_welcome_email_client_task, send_welcome_email_driver_task, send_driver_approval_email_task, send_ride_confirmation_email_task, send_ride_completion_email_task
from core.utils import send_welcome_email_client, send_welcome_email_driver, send_driver_approval_email, send_ride_confirmation_email, send_ride_completion_email
from accounts.models import DriverProfile
import json


class Command(BaseCommand):
    help = 'Test welcome email functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to send welcome email to',
        )
        parser.add_argument(
            '--driver-id',
            type=int,
            help='Driver ID to send welcome email to',
        )
        parser.add_argument(
            '--test-approval',
            action='store_true',
            help='Test driver approval email',
        )
        parser.add_argument(
            '--test-ride-confirmation',
            action='store_true',
            help='Test ride confirmation email',
        )
        parser.add_argument(
            '--test-ride-completion',
            action='store_true',
            help='Test ride completion email',
        )
        parser.add_argument(
            '--ride-id',
            type=int,
            help='Ride ID to send confirmation email for',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Send email asynchronously using Celery',
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List available users and drivers',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        if options['list_users']:
            self.list_users_and_drivers()
            return
        
        if options['email']:
            self.test_with_email(options['email'], options['async'])
            return
        
        if options['user_id']:
            self.test_client_welcome(options['user_id'], options['async'])
            return
        
        if options['driver_id']:
            if options['test_approval']:
                self.test_driver_approval(options['driver_id'], options['async'])
            else:
                self.test_driver_welcome(options['driver_id'], options['async'])
            return
        
        if options['ride_id'] and options['test_ride_confirmation']:
            self.test_ride_confirmation(options['ride_id'], options['async'])
            return
        
        if options['ride_id'] and options['test_ride_completion']:
            self.test_ride_completion(options['ride_id'], options['async'])
            return
        
        # Default: test with first available user
        self.test_default()

    def list_users_and_drivers(self):
        """List available users and drivers for testing"""
        User = get_user_model()
        
        self.stdout.write(self.style.SUCCESS('Available Users:'))
        users = User.objects.all()[:10]  # Limit to first 10
        for user in users:
            self.stdout.write(f"  ID: {user.id} | Email: {user.email} | Name: {user.get_full_name() or user.username}")
        
        self.stdout.write(self.style.SUCCESS('\nAvailable Drivers:'))
        drivers = DriverProfile.objects.all()[:10]  # Limit to first 10
        for driver in drivers:
            self.stdout.write(f"  ID: {driver.id} | Email: {driver.user.email} | Name: {driver.user.get_full_name() or driver.user.username}")
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found. Create a user first.'))
        if not drivers.exists():
            self.stdout.write(self.style.WARNING('No drivers found. Create a driver first.'))

    def test_with_email(self, email, use_async):
        """Test with a specific email address"""
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f'Found user: {user.get_full_name() or user.username}'))
            
            if use_async:
                self.stdout.write('Sending welcome email asynchronously...')
                result = send_welcome_email_client_task.delay(user.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending welcome email synchronously...')
                success = send_welcome_email_client(user)
                if success:
                    self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send welcome email'))
                    
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} not found'))

    def test_client_welcome(self, user_id, use_async):
        """Test client welcome email"""
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(self.style.SUCCESS(f'Testing client welcome email for: {user.get_full_name() or user.username} ({user.email})'))
            
            if use_async:
                self.stdout.write('Sending welcome email asynchronously...')
                result = send_welcome_email_client_task.delay(user.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending welcome email synchronously...')
                success = send_welcome_email_client(user)
                if success:
                    self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send welcome email'))
                    
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))

    def test_driver_welcome(self, driver_id, use_async):
        """Test driver welcome email"""
        try:
            driver = DriverProfile.objects.get(id=driver_id)
            self.stdout.write(self.style.SUCCESS(f'Testing driver welcome email for: {driver.user.get_full_name() or driver.user.username} ({driver.user.email})'))
            
            if use_async:
                self.stdout.write('Sending welcome email asynchronously...')
                result = send_welcome_email_driver_task.delay(driver.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending welcome email synchronously...')
                success = send_welcome_email_driver(driver)
                if success:
                    self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send welcome email'))
                    
        except DriverProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Driver with ID {driver_id} not found'))

    def test_driver_approval(self, driver_id, use_async):
        """Test driver approval email"""
        try:
            driver = DriverProfile.objects.get(id=driver_id)
            self.stdout.write(self.style.SUCCESS(f'Testing driver approval email for: {driver.user.get_full_name() or driver.user.username} ({driver.user.email})'))
            
            if use_async:
                self.stdout.write('Sending driver approval email asynchronously...')
                result = send_driver_approval_email_task.delay(driver.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending driver approval email synchronously...')
                success = send_driver_approval_email(driver)
                if success:
                    self.stdout.write(self.style.SUCCESS('Driver approval email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send driver approval email'))
                    
        except DriverProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Driver with ID {driver_id} not found'))

    def test_ride_confirmation(self, ride_id, use_async):
        """Test ride confirmation email"""
        from rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=ride_id)
            self.stdout.write(self.style.SUCCESS(f'Testing ride confirmation email for: Ride #{ride.id} - {ride.client.user.get_full_name() or ride.client.user.username} ({ride.client.user.email})'))
            
            if use_async:
                self.stdout.write('Sending ride confirmation email asynchronously...')
                result = send_ride_confirmation_email_task.delay(ride.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending ride confirmation email synchronously...')
                success = send_ride_confirmation_email(ride)
                if success:
                    self.stdout.write(self.style.SUCCESS('Ride confirmation email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send ride confirmation email'))
                    
        except Ride.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Ride with ID {ride_id} not found'))

    def test_ride_completion(self, ride_id, use_async):
        """Test ride completion email"""
        from rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=ride_id)
            self.stdout.write(self.style.SUCCESS(f'Testing ride completion email for: Ride #{ride.id} - {ride.client.user.get_full_name() or ride.client.user.username} ({ride.client.user.email})'))
            
            if use_async:
                self.stdout.write('Sending ride completion email asynchronously...')
                result = send_ride_completion_email_task.delay(ride.id)
                self.stdout.write(self.style.SUCCESS(f'Task queued with ID: {result.id}'))
            else:
                self.stdout.write('Sending ride completion email synchronously...')
                success = send_ride_completion_email(ride)
                if success:
                    self.stdout.write(self.style.SUCCESS('Ride completion email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send ride completion email'))
                    
        except Ride.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Ride with ID {ride_id} not found'))

    def test_default(self):
        """Test with first available user"""
        User = get_user_model()
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Testing with first user: {user.get_full_name() or user.username} ({user.email})'))
        self.stdout.write('Sending welcome email synchronously...')
        
        success = send_welcome_email_client(user)
        if success:
            self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Failed to send welcome email'))
        
        # Also test async
        self.stdout.write('\nTesting async version...')
        result = send_welcome_email_client_task.delay(user.id)
        self.stdout.write(self.style.SUCCESS(f'Async task queued with ID: {result.id}'))
        
        self.stdout.write(self.style.SUCCESS('\nTest completed! Check your email inbox.'))
        
        # Also test driver approval email if drivers exist
        driver = DriverProfile.objects.first()
        if driver:
            self.stdout.write(self.style.SUCCESS(f'\nTesting driver approval email with: {driver.user.get_full_name() or driver.user.username} ({driver.user.email})'))
            success = send_driver_approval_email(driver)
            if success:
                self.stdout.write(self.style.SUCCESS('Driver approval email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to send driver approval email'))
