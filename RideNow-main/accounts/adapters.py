import logging
import traceback

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse


from .models import User, ClientProfile, DriverProfile, UserPreferences, UserSecuritySettings, UserActivityLog

logger = logging.getLogger(__name__)

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Save user from social login and create CLIENT profile ONLY.
        Social login is for riders/clients only. Drivers must use traditional registration
        with document verification.
        """
        try:
            # Get the social account data
            social_account = sociallogin.account
            provider = social_account.provider
            extra_data = social_account.extra_data
            
            # Extract user data based on provider
            if provider == 'google':
                email = extra_data.get('email')
                first_name = extra_data.get('given_name', '')
                last_name = extra_data.get('family_name', '')
                profile_picture = extra_data.get('picture', '')
            elif provider == 'apple':
                email = extra_data.get('email')
                name_data = extra_data.get('name', {})
                first_name = name_data.get('firstName', '') if name_data else ''
                last_name = name_data.get('lastName', '') if name_data else ''
                profile_picture = ''
            else:
                email = sociallogin.user.email
                first_name = sociallogin.user.first_name or ''
                last_name = sociallogin.user.last_name or ''
                profile_picture = ''
            
            # Create or get the user
            user = sociallogin.user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            
            # Generate unique username if needed
            if not user.username:
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user.username = username
            
            user.save()
            
            # ALWAYS create CLIENT profile for social logins (never driver)
            # Drivers must use traditional registration with document verification
            if not hasattr(user, 'client_profile'):
                client_profile, created = ClientProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'username': user.username,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_verified': True,  # Social logins are pre-verified by provider
                        'is_active': True,
                    }
                )
                
                if created:
                    # Set user as client
                    user.is_client = True
                    user.is_driver = False  # Explicitly set to False
                    user.save()
                    logger.info(f"Created CLIENT profile for social login user: {user.email} via {provider}")
                    
                    # Add welcome message
                    messages.success(request, f"Welcome to Zyra! Your account has been created successfully via {provider.title()}.")
            
            # Create user preferences and security settings
            UserPreferences.objects.get_or_create(user=user)
            UserSecuritySettings.objects.get_or_create(user=user)
            
            # Log the social login activity
            try:
                UserActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    description=f'Social login via {provider} (Client)',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    device_info={
                        'provider': provider,
                        'social_id': social_account.uid,
                        'profile_picture': profile_picture,
                        'account_type': 'client'
                    }
                )
            except Exception as log_error:
                logger.error(f"Error logging social login activity: {str(log_error)}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error in social account adapter: {str(e)}")
            logger.error(traceback.format_exc())
            # Fall back to default behavior
            return super().save_user(request, sociallogin, form)
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Allow auto signup for social logins
        """
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed
        """
        # If user is already logged in, link the account
        if request.user.is_authenticated:
            return
        
        # Check if user with this email already exists
        try:
            user = User.objects.get(email=sociallogin.user.email)
            # Connect this social account to the existing user
            sociallogin.connect(request, user)
            logger.info(f"Connected social account {sociallogin.account.provider} to existing user {user.email}")
        except User.DoesNotExist:
            pass
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Redirect after connecting social account
        """
        return reverse('profile')
    
    def get_login_redirect_url(self, request):
        """
        Redirect after successful social login.
        Social logins always create CLIENT accounts, so redirect to booking page.
        """
        # Check if user has a specific redirect in session
        next_url = request.session.get('next')
        if next_url:
            return next_url
        
        # Social logins are always clients, redirect to ride booking
        return reverse('rides:book_ride')
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Handle authentication errors
        """
        logger.error(f"Social authentication error for {provider_id}: {error}")
        logger.error(f"Exception: {exception}")
        messages.error(request, f"Authentication failed with {provider_id}. Please try again or use a different method.")
        return super().authentication_error(request, provider_id, error, exception, extra_context)


class AccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for allauth
    """
    
    def get_login_redirect_url(self, request):
        """
        Redirect after successful login
        """
        # Check if user has a specific redirect in session
        next_url = request.session.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        
        # Default redirect based on user type
        user = request.user
        if hasattr(user, 'driver_profile') and user.is_driver:
            return reverse('rides:driver_dashboard')
        elif hasattr(user, 'client_profile') and user.is_client:
            return reverse('rides:book_ride')
        else:
            return reverse('profile')
    
    def get_signup_redirect_url(self, request):
        """
        Redirect after successful signup
        """
        return self.get_login_redirect_url(request)
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user from traditional signup
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set default values
        user.is_active = True
        
        if commit:
            user.save()
        
        return user