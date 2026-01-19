from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser or reset admin credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superuser',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
        )
        parser.add_argument(
            '--reset-password',
            type=str,
            help='Reset password for existing user by email',
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all users',
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_users()
        elif options['reset_password']:
            self.reset_password(options['reset_password'])
        else:
            self.create_superuser(
                options.get('email'),
                options.get('username'),
                options.get('password')
            )

    def create_superuser(self, email=None, username=None, password=None):
        """Create a new superuser"""
        if not email:
            email = input("Enter email address: ").strip()
        
        if not email:
            self.stdout.write(self.style.ERROR("Email is required!"))
            return
        
        if not username:
            username = email.split('@')[0]
        
        if not password:
            password = input("Enter password: ").strip()
        
        if not password:
            self.stdout.write(self.style.ERROR("Password is required!"))
            return
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f"User with email {email} already exists!")
                    )
                    choice = input("Do you want to make them a superuser? (y/n): ").strip().lower()
                    if choice == 'y':
                        user = User.objects.get(email=email)
                        user.is_staff = True
                        user.is_superuser = True
                        user.set_password(password)
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ User {email} is now a superuser!")
                        )
                    else:
                        self.stdout.write("Operation cancelled.")
                    return
                
                # Create new superuser
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS("✅ Superuser created successfully!"))
                self.stdout.write(f"Email: {email}")
                self.stdout.write(f"Username: {username}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating superuser: {e}"))

    def list_users(self):
        """List all users"""
        self.stdout.write("\n=== All Users ===")
        users = User.objects.all()
        if not users:
            self.stdout.write("No users found.")
            return
        
        for user in users:
            status = []
            if user.is_superuser:
                status.append("Superuser")
            if user.is_staff:
                status.append("Staff")
            if user.is_active:
                status.append("Active")
            else:
                status.append("Inactive")
            
            self.stdout.write(f"ID: {user.id}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Phone: {user.phone_number or 'Not set'}")
            self.stdout.write(f"Status: {', '.join(status)}")
            self.stdout.write("-" * 40)

    def reset_password(self, email):
        """Reset password for existing user"""
        try:
            user = User.objects.get(email=email)
            new_password = input("Enter new password: ").strip()
            if not new_password:
                self.stdout.write(self.style.ERROR("Password is required!"))
                return
            
            user.set_password(new_password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✅ Password reset successfully for {email}")
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ User with email {email} not found!")
            )
