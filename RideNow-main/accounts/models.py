# import os
# import math
# import uuid
import string
import random
import datetime
from datetime import date
from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser
from core.image_processor import CompressedImageField
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


from .managers import CustomUserManager
from core.tasks import create_profile

from core.validators import post_file_extension, validate_image_with_face

from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    is_client = models.BooleanField(default=False, help_text=_('Designate the user as a client'))
    is_driver = models.BooleanField(default=False, help_text=_('Designate the user as a diver'))
    is_banned = models.BooleanField(default=False, help_text=_('Ban accounts that breach user guidelines'))
    referral_code = models.UUIDField(null=True, blank=True, editable=False)

    REQUIRED_FIELDS = ['email',]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])
    
    def get_referral_url(self):
        return reverse('referred_signup', args=[self.referral_code])
    
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

    def get_user_profile(self):
        if self.is_client:
            try:
                profile = self.client_profile 
            except ClientProfile.DoesNotExist:
                profile = None
        elif self.is_driver:
            try:
                profile = self.driver_profile
            except DriverProfile.DoesNotExist:
                profile = None
        else:
            profile = None
        return profile

    # @property
    # def check_active_subscription(self):
    #     from finance.models import Subscription
    #     if Subscription.objects.filter(user__id=self.id, is_active=True).exists():
    #         return True
    #     else:
    #         return False
        
    # @property
    # def user_subscription(self, request):
    #     from finance.models import Subscription
    #     try:
    #         subscription = Subscription.objects.get(user__id=self.id, is_active=True)
    #         return subscription
    #     except Subscription.DoesNotExist:
    #         messages.error(request, 'You do not have active subscription!')
    #         return
        
    @property
    def get_user_names(self):
        if self.first_name and self.last_name:
            name = f'{self.first_name} {self.last_name}'
        elif self.first_name:
            name = f'{self.first_name}'
        elif self.last_name:
            name = f'{self.last_name}'
        elif self.username:
            name = f'{self.username}'
        else:
            name = 'User'
        return name


    def save(self, *args, **kwargs):
        # create_profile.apply_async(args=[self.pk,])
        # if User.objects.filter(user__id=self.id).exists():
        #     pass
        # else:
        #     User.objects.create(user=self, username=self.username, first_name=self.username, last_name="New User", email=self.email)
        super(User, self).save(*args, **kwargs)


GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()

    def __str__(self):
        return f"{self.username or 'Unknown'} - {'Success' if self.success else 'Failed'}"

class ClientProfile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, models.CASCADE, related_name="client_profile")
    username = models.CharField(max_length=75, unique=True)
    unique_id = models.CharField(max_length=9, help_text='User Unique ID', editable=False, default='000000001')
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75, null=True, blank=True)
    other_name = models.CharField(max_length=75, blank=True, null=True)
    photo = CompressedImageField(null=True, blank=True, quality=80, upload_to='users/%Y/%m/%d', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    cover_photo = CompressedImageField(null=True, quality=80, upload_to='users/%Y/%m/%d', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    email = models.EmailField()
    email_confirmed = models.BooleanField(default=False)
    phone = PhoneNumberField(null=True, blank=True, help_text='Follow syntax; start e.g +256')
    country = CountryField(blank_label='(Select Country)', verbose_name=_("Country"), help_text=_("Country of residence"), default='UG')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=75, default="Kampala")
    bio = models.TextField(blank=True, null=True, help_text=_("Hint: What inspires you, what's good about you"))
    interests = models.CharField(max_length=175, blank=True, null=True, help_text=_("e.g Sports, Travel, Vlogging, Engineering, Medicine"))
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False, help_text=_("Ban User Profile"))
    is_online = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


    # def __unicode__(self):
    #     return unicode(self.username)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user_profile', args=[str(self.id)])

    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.unique_id)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False
        
    def age(self):
        age = (date.today() - self.date_of_birth).days / 365
        return round(age)

    def generate_unique_number(self):
        precede_numbers = '012'
        numbers = '3456789'
        alphanumeric = precede_numbers + numbers
        length = 9
        generate_unique_number = "".join(random.sample(alphanumeric, length))
        while ClientProfile.objects.filter(unique_id=generate_unique_number).exists():
            generate_unique_number = "".join(random.sample(alphanumeric, length))
            # return generate_unique_number
        return generate_unique_number
    
    def get_user_currency(self):
        import pycountry
        country_name = self.country.name
        country = pycountry.countries.get(name=country_name)
        currency = pycountry.currencies.get(numeric=country.numeric)
        return currency.alpha_3

    def save(self, *args, **kwargs):
        if self.unique_id == '000000001':
            self.unique_id = self.generate_unique_number()

        if not self.email and hasattr(self.user, 'email'):
            self.email = self.user.email
        if not self.phone and hasattr(self.user, 'phone_number'):
            self.phone = self.user.phone_number
        if not self.username and hasattr(self.user, 'username'):
            self.username = self.user.username
        if not self.first_name and hasattr(self.user, 'first_name'):
            self.first_name = self.user.first_name
        if not self.last_name and hasattr(self.user, 'last_name'):
            self.last_name = self.user.last_name
        if not self.other_name and hasattr(self.user, 'other_name'):
            self.other_name = self.user.other_name
        super(ClientProfile, self).save(*args, **kwargs)

class ClientRating(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0, verbose_name=("Star Ratings"), help_text="Give star rating")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.username} - {self.rating}"
    
    def save(self, *args, **kwargs):
        super(ClientRating, self).save(*args, **kwargs)


class DriverProfile(models.Model):
    DRIVER_STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('away', 'Away'),
        ('offline', 'Offline'),
    ]
    user = models.OneToOneField(AUTH_USER_MODEL, models.CASCADE, related_name="driver_profile")
    username = models.CharField(max_length=75, unique=True)
    unique_id = models.CharField(max_length=9, help_text='User Unique ID', editable=False, default='000000001')
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75, null=True, blank=True)
    other_name = models.CharField(max_length=75, blank=True, null=True)
    photo = CompressedImageField(null=True, blank=True, quality=80, upload_to='users/%Y/%m/%d', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    cover_photo = CompressedImageField(null=True, quality=80, upload_to='users/%Y/%m/%d', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    email = models.EmailField()
    email_confirmed = models.BooleanField(default=False)
    phone = PhoneNumberField(null=True, blank=True, help_text='Follow syntax; start e.g +256')
    country = CountryField(blank_label='(Select Country)', verbose_name=_("Country"), help_text=_("Country of residence"), default='UG')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=75, default="Kampala")
    bio = models.TextField(blank=True, null=True, help_text=_("Hint: What inspires you, what's good about you"))
    vehicle_registration = models.CharField(max_length=15)
    drivers_license_no = models.CharField(max_length=15, null=True, blank=True)
    driver_status = models.CharField(max_length=10, choices=DRIVER_STATUS_CHOICES, default='available')
    is_approved = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False, help_text=_("Ban User Profile"))
    is_online = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)



    # def __unicode__(self):
    #     return unicode(self.username)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user_profile', args=[str(self.id)])

    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.unique_id)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False
        
    def number_of_likes(self):
        return self.user_likes.count()
    
    def match_profiles(self):
        # Get all other profiles excluding the user's own profile
        if self.gender is not None:
            if self.gender == 'M':
                search_gender = 'F'
            elif self.gender == 'F':
                search_gender = 'M'
            other_profiles = DriverProfile.objects.filter(user__is_active=True, user__is_banned=False, is_banned=False, country=self.country, gender__iexact=search_gender).exclude(user=self.user)
            age = self.age()
            # Example algorithm: Matching based on common interests and age difference
            matches = []
            for profile in other_profiles:
                if self.interests is not None:
                    user_age = profile.age()
                    age_difference = abs(age - user_age)
                    if profile.interests:
                        common_interests = set(self.interests) & set(profile.interests)
                        # Customize the matching criteria based on your requirements
                        if len(common_interests) >= 2 and age_difference <= 5:
                            matches.append(profile)
                    else:
                        if age_difference <= 5:
                            matches.append(profile)
            return matches
        else:
            return redirect('update_profile', self.id)
    

    def age(self):
        age = (date.today() - self.date_of_birth).days / 365
        return round(age)

    def generate_unique_number(self):
        precede_numbers = '012'
        numbers = '3456789'
        alphanumeric = precede_numbers + numbers
        length = 9
        generate_unique_number = "".join(random.sample(alphanumeric, length))
        while DriverProfile.objects.filter(unique_id=generate_unique_number).exists():
            generate_unique_number = "".join(random.sample(alphanumeric, length))
            # return generate_unique_number
        return generate_unique_number
    
    def get_user_currency(self):
        import pycountry
        country_name = self.country.name
        country = pycountry.countries.get(name=country_name)
        currency = pycountry.currencies.get(numeric=country.numeric)
        return currency.alpha_3

    def save(self, *args, **kwargs):
        if self.unique_id == '000000001':
            self.unique_id = self.generate_unique_number()

        if not self.email and hasattr(self.user, 'email'):
            self.email = self.user.email
        if not self.phone and hasattr(self.user, 'phone_number'):
            self.phone = self.user.phone_number
        if not self.username and hasattr(self.user, 'username'):
            self.username = self.user.username
        if not self.first_name and hasattr(self.user, 'first_name'):
            self.first_name = self.user.first_name
        if not self.last_name and hasattr(self.user, 'last_name'):
            self.last_name = self.user.last_name
        if not self.other_name and hasattr(self.user, 'other_name'):
            self.other_name = self.user.other_name
        super(DriverProfile, self).save(*args, **kwargs)
    


class ReportUser(models.Model):
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_user')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reporter')
    complaint = models.TextField()
    is_attended_to = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reported User'
        verbose_name_plural = 'Reported Users'

    def __str__(self):
        return str(f'Reported User {self.reported_user}')
    

class ReportEvidence(models.Model):
    report = models.ForeignKey(ReportUser, on_delete=models.CASCADE, related_name='report_evidence')
    file = models.FileField(upload_to='ReportEvidence/%Y/%m/%d')
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f'Report Evidence {self.id}')
    

class VerificationToken(models.Model):
    TOKEN_TYPES = [
        ('EMAIL_VERIFICATION', 'Email Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_tokens")
    token = models.CharField(max_length=64, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES, default='EMAIL_VERIFICATION')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            if self.token_type == 'EMAIL_VERIFICATION':
                # Generate 6 digit token for email verification
                while True:
                    token = ''.join(random.choices(string.digits, k=6))
                    if not VerificationToken.objects.filter(token=token).exists():
                        self.token = token
                        break
            else:
                # Generate 64 character secure token for password reset
                while True:
                    token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
                    if not VerificationToken.objects.filter(token=token).exists():
                        self.token = token
                        break
        
        if not self.expires_at:
            if self.token_type == 'EMAIL_VERIFICATION':
                # Email verification tokens expire in 24 hours
                self.expires_at = timezone.now() + timedelta(hours=24)
            else:
                # Password reset tokens expire in 1 hour
                self.expires_at = timezone.now() + timedelta(hours=1)
        
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()

    def __str__(self):
        return f"{self.get_token_type_display()} token for {self.user.username}"


class TermsAcceptance(models.Model):
    """Track user acceptance of Terms of Service"""
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='terms_acceptance')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    terms_version = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Terms Acceptance'
        verbose_name_plural = 'Terms Acceptances'
    
    def __str__(self):
        return f'{self.user.username} - {self.accepted_at}'


class UserPreferences(models.Model):
    """User preferences and settings"""
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True, help_text='Receive email notifications')
    sms_notifications = models.BooleanField(default=True, help_text='Receive SMS notifications')
    push_notifications = models.BooleanField(default=True, help_text='Receive push notifications')
    marketing_emails = models.BooleanField(default=False, help_text='Receive marketing emails')
    
    # Privacy settings
    PROFILE_VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
    ]
    profile_visibility = models.CharField(
        max_length=10, 
        choices=PROFILE_VISIBILITY_CHOICES, 
        default='public',
        help_text='Who can see your profile'
    )
    
    # Language and region
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sw', 'Swahili'),
        ('lg', 'Luganda'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
    ]
    language = models.CharField(
        max_length=5, 
        choices=LANGUAGE_CHOICES, 
        default='en',
        help_text='Preferred language'
    )
    
    TIMEZONE_CHOICES = [
        ('Africa/Kampala', 'Africa/Kampala (EAT)'),
        ('Africa/Nairobi', 'Africa/Nairobi (EAT)'),
        ('Africa/Dar_es_Salaam', 'Africa/Dar_es_Salaam (EAT)'),
        ('Africa/Addis_Ababa', 'Africa/Addis_Ababa (EAT)'),
        ('Africa/Kigali', 'Africa/Kigali (CAT)'),
        ('Africa/Bujumbura', 'Africa/Bujumbura (CAT)'),
        ('Africa/Lagos', 'Africa/Lagos (WAT)'),
        ('Africa/Cairo', 'Africa/Cairo (EET)'),
        ('Africa/Johannesburg', 'Africa/Johannesburg (SAST)'),
        ('Europe/London', 'Europe/London (GMT)'),
        ('America/New_York', 'America/New_York (EST)'),
        ('America/Los_Angeles', 'America/Los_Angeles (PST)'),
    ]
    timezone = models.CharField(
        max_length=50, 
        choices=TIMEZONE_CHOICES, 
        default='Africa/Kampala',
        help_text='Preferred timezone'
    )
    
    # Ride preferences
    preferred_payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('mobile_money', 'Mobile Money'),
            ('card', 'Card'),
            ('wallet', 'Wallet'),
        ],
        default='cash',
        help_text='Preferred payment method for rides'
    )
    
    # Driver-specific preferences
    auto_accept_rides = models.BooleanField(
        default=False, 
        help_text='Automatically accept ride requests (drivers only)'
    )
    max_ride_distance = models.PositiveIntegerField(
        default=50, 
        help_text='Maximum ride distance in kilometers (drivers only)'
    )
    preferred_ride_types = models.CharField(
        max_length=200,
        blank=True,
        help_text='Preferred ride types (comma-separated)'
    )
    
    # Client-specific preferences
    preferred_driver_rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        default=4.0,
        help_text='Minimum driver rating preference (clients only)'
    )
    preferred_vehicle_type = models.CharField(
        max_length=20,
        choices=[
            ('any', 'Any'),
            ('sedan', 'Sedan'),
            ('suv', 'SUV'),
            ('hatchback', 'Hatchback'),
            ('motorcycle', 'Motorcycle'),
        ],
        default='any',
        help_text='Preferred vehicle type (clients only)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f'Preferences for {self.user.username}'
    
    def save(self, *args, **kwargs):
        # Ensure only drivers can set driver-specific preferences
        if not self.user.is_driver:
            self.auto_accept_rides = False
            self.max_ride_distance = 50
            self.preferred_ride_types = ''
        
        # Ensure only clients can set client-specific preferences
        if not self.user.is_client:
            self.preferred_driver_rating = 4.0
            self.preferred_vehicle_type = 'any'
        
        super().save(*args, **kwargs)


class UserSecuritySettings(models.Model):
    """User security settings and configurations"""
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='security_settings')
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False, help_text='Two-factor authentication enabled')
    two_factor_secret = models.CharField(max_length=32, blank=True, help_text='2FA secret key')
    backup_codes = models.JSONField(default=list, blank=True, help_text='2FA backup codes')
    
    # Login security
    login_alerts = models.BooleanField(default=True, help_text='Receive login alerts')
    session_timeout = models.PositiveIntegerField(
        default=60, 
        help_text='Session timeout in minutes'
    )
    max_concurrent_sessions = models.PositiveIntegerField(
        default=3, 
        help_text='Maximum concurrent sessions'
    )
    
    # Password security
    password_changed_at = models.DateTimeField(auto_now_add=True, help_text='Last password change')
    password_expires_at = models.DateTimeField(null=True, blank=True, help_text='Password expiration date')
    require_password_change = models.BooleanField(default=False, help_text='Require password change on next login')
    
    # Account security
    account_locked = models.BooleanField(default=False, help_text='Account locked due to security reasons')
    account_locked_until = models.DateTimeField(null=True, blank=True, help_text='Account locked until')
    failed_login_attempts = models.PositiveIntegerField(default=0, help_text='Failed login attempts')
    last_failed_login = models.DateTimeField(null=True, blank=True, help_text='Last failed login attempt')
    
    # Privacy and data
    data_sharing_consent = models.BooleanField(default=False, help_text='Consent to share data with partners')
    analytics_consent = models.BooleanField(default=True, help_text='Consent to analytics tracking')
    location_tracking = models.BooleanField(default=True, help_text='Allow location tracking')
    
    # API and third-party access
    api_access_enabled = models.BooleanField(default=False, help_text='Enable API access')
    api_key = models.CharField(max_length=64, blank=True, help_text='API access key')
    api_key_created_at = models.DateTimeField(null=True, blank=True, help_text='API key creation date')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Security Settings'
        verbose_name_plural = 'User Security Settings'
    
    def __str__(self):
        return f'Security settings for {self.user.username}'
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.account_locked:
            return False
        
        if self.account_locked_until and timezone.now() > self.account_locked_until:
            # Unlock account if lock period has expired
            self.account_locked = False
            self.account_locked_until = None
            self.failed_login_attempts = 0
            self.save()
            return False
        
        return True
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.account_locked = True
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save()
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save()
    
    def generate_api_key(self):
        """Generate a new API key"""
        import secrets
        self.api_key = secrets.token_urlsafe(32)
        self.api_key_created_at = timezone.now()
        self.save()
        return self.api_key
    
    def revoke_api_key(self):
        """Revoke API access"""
        self.api_key = ''
        self.api_key_created_at = None
        self.api_access_enabled = False
        self.save()


class UserActivityLog(models.Model):
    """Log user activities for security and audit purposes"""
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('security_settings_update', 'Security Settings Update'),
        ('preferences_update', 'Preferences Update'),
        ('account_deletion', 'Account Deletion'),
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(help_text='Activity description')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, help_text='Geographic location')
    device_info = models.JSONField(default=dict, blank=True, help_text='Device information')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_activity_type_display()} - {self.created_at}'


class UserSession(models.Model):
    """Track user sessions for security purposes"""
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text='Session expiration time')
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f'{self.user.username} - {self.session_key[:8]}...'
    
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at
    
    def extend_session(self, minutes=60):
        """Extend session expiration"""
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save()
