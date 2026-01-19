from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier for authentication instead of usernames.
    """
    def create_user(self, email, phone_number=None, username=None, **extra_fields):
        """
        Create and save a User with the given email, phone_number, and username.
        """
        if not email:
            raise ValueError(_('The Email must be set.'))
        
        # Only require phone_number for regular users, not superusers
        if not phone_number and not extra_fields.get('is_superuser'):
            raise ValueError(_('The Phone Number must be set.'))
        
        email = self.normalize_email(email)
        if not username:
            username = email.split('@')[0]  # Generate a default username from the email
        
        user = self.model(email=email, phone_number=phone_number, username=username, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number=None, username=None, **extra_fields):
        """
        Create and save a SuperUser with the given email, phone_number, and username.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # Superusers don't require phone numbers
        return self.create_user(email, phone_number, username, **extra_fields)
