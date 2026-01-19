import logging
import random
import traceback

# Django core and utilities
from django.conf import settings
from django.contrib import messages
from django.contrib import auth
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import (
    ProfileUpdateForm, DriverProfileUpdateForm, PhotoUpdateForm, 
    DriverPhotoUpdateForm, PreferencesForm, SecurityForm, 
    AccountDeletionForm, CustomPasswordChangeForm
)
from .models import UserPreferences, UserSecuritySettings, UserActivityLog
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_protect
from django.http import (
    HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login, logout, authenticate, get_user_model,
    views as auth_views,
    decorators as auth_decorators
)
from django.views.generic import (
    CreateView, TemplateView, UpdateView, DeleteView, DetailView
)

# Third-party and REST framework
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# App-specific imports
from core.models import OTP
from core.models import ErrorLogs
from finance.models import Receipt
from tracking_analyzer.models import Tracker
from .serializers import LoginSerializer
from .models import User, ClientProfile, DriverProfile
from core.utils import SendOTP, send_email_alert, send_sms_alert


logger = logging.getLogger(__name__)


# Helper function for sending verification token (implement using your email/SMS provider)
def send_verification(user, token):
    """Send verification token to user via email and SMS"""
    from core.tasks import send_email_task, send_sms_alert_task
    try:
        # Send email verification
        send_email_task.delay(
            email=user.email,
            subject="Verify Your Daraza WiFi Manager Account",
            message=(
                f"Dear {user.email},\n\n"
                f"Thank you for registering with Daraza WiFi Manager. Your verification code is:\n\n"
                f"{token}\n\n"
                "Please enter this code in the verification page to activate your account.\n\n"
                "If you did not request this verification, please ignore this message.\n\n"
                "For support, contact us at support@daraza.net or call +256789079301.\n\n"
                "Best regards,\n"
                "The Daraza Team"
            )
        )

        # Send SMS verification
        if user.phone: 
            send_sms_alert_task.delay(
                body=f"Your Daraza WiFi Manager verification code is: {token}",
                sms_phone=user.phone
            )
    except Exception as e:
        ErrorLogs.objects.create(
            error_narration=f"Error sending verification: {str(e)}",
            stack_trace=traceback.format_exc()
        )


def signup(request):
    return render(request, 'accounts/signup.html')

def login_user(request):
    return render(request, 'accounts/login.html')


@csrf_protect 
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')
    return HttpResponseNotAllowed(["POST"])


@extend_schema(exclude=True)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        username_or_email_or_phone = serializer.validated_data['username_or_email_or_phone']
        password = serializer.validated_data['password']

        # Try to authenticate with username first (for backward compatibility)
        user = authenticate(request, username=username_or_email_or_phone, password=password)
        
        # If not found, try email or phone
        if user is None:
            try:
                if '@' in username_or_email_or_phone:
                    user = User.objects.get(email=username_or_email_or_phone)
                else:
                    user = User.objects.get(phone=username_or_email_or_phone)
                
                user = authenticate(request, username=user.username, password=password)
            except ObjectDoesNotExist:
                return Response(
                    {"detail": "Invalid credentials."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Update user profile with data from User and Employee models
            from .signals import sync_user_profile_from_related_models
            sync_user_profile_from_related_models(user)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'redirect_url': '/accounts/user_account/'
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"detail": "Invalid credentials."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

# AJAX-based logout
def auto_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({"message": "Logged out due to inactivity"}, status=200)
    return JsonResponse({"message": "Already logged out"}, status=400)


def refresh_session(request):
    if request.user.is_authenticated:
        request.session.modified = True  # Extends session expiration
        return JsonResponse({"message": "Session refreshed", "timestamp": now().isoformat()})
    return JsonResponse({"message": "Not authenticated"}, status=401)



def check_user_email(request):
	email = request.GET.get('email')
	data = {
	   'email_exists': User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)


@login_required
def profile_management(request):
    """Comprehensive profile management page"""
    user = request.user
    
    try:
        if user.is_client:
            profile = ClientProfile.objects.get(user=user)
        elif user.is_driver:
            profile = DriverProfile.objects.get(user=user)
        else:
            messages.error(request, 'Invalid user type.')
            return redirect('login')
        
        # Get or create user preferences and security settings
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        security_settings, created = UserSecuritySettings.objects.get_or_create(user=user)
            
        context = {
            'profile': profile,
            'user': user,
            'preferences': preferences,
            'security_settings': security_settings,
        }
        return render(request, 'accounts/profile_management.html', context)
        
    except (ClientProfile.DoesNotExist, DriverProfile.DoesNotExist):
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('login')
    except Exception as e:
        logger.error(f"Error in profile management view: {e}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('login')

@login_required
def update_profile(request):
    """Update profile information"""
    if request.method != 'POST':
        return redirect('profile')
    
    user = request.user
    
    try:
        if user.is_client:
            profile = ClientProfile.objects.get(user=user)
            form_class = ProfileUpdateForm
        elif user.is_driver:
            profile = DriverProfile.objects.get(user=user)
            form_class = DriverProfileUpdateForm
        else:
            messages.error(request, 'Invalid user type.')
            return redirect('profile')
        
        form = form_class(request.POST, instance=profile)
        
        if form.is_valid():
            # Update user model fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone']
            user.save()
            
            # Update profile
            form.save()
            
            messages.success(request, 'Profile updated successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
                    
    except (ClientProfile.DoesNotExist, DriverProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        messages.error(request, 'An error occurred while updating your profile.')
    
    return redirect('profile')

@login_required
def update_photos(request):
    """Update profile and cover photos"""
    if request.method != 'POST':
        return redirect('profile')
    
    user = request.user
    
    try:
        if user.is_client:
            profile = ClientProfile.objects.get(user=user)
            form_class = PhotoUpdateForm
        elif user.is_driver:
            profile = DriverProfile.objects.get(user=user)
            form_class = DriverPhotoUpdateForm
        else:
            messages.error(request, 'Invalid user type.')
            return redirect('profile')
        
        form = form_class(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Photos updated successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
                    
    except (ClientProfile.DoesNotExist, DriverProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
    except Exception as e:
        logger.error(f"Error updating photos: {e}")
        messages.error(request, 'An error occurred while updating your photos.')
    
    return redirect('profile')

@login_required
def update_preferences(request):
    """Update user preferences"""
    if request.method != 'POST':
        return redirect('profile')
    
    try:
        user = request.user
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        
        form = PreferencesForm(request.POST, instance=preferences)
        
        if form.is_valid():
            form.save()
            
            # Log activity
            UserActivityLog.objects.create(
                user=user,
                activity_type='preferences_update',
                description='User preferences updated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Preferences updated successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        messages.error(request, 'An error occurred while updating your preferences.')
    
    return redirect('profile')

@login_required
def update_security(request):
    """Update security settings"""
    if request.method != 'POST':
        return redirect('profile')
    
    try:
        user = request.user
        security_settings, created = UserSecuritySettings.objects.get_or_create(user=user)
        
        form = SecurityForm(request.POST, instance=security_settings)
        
        if form.is_valid():
            form.save()
            
            # Update session timeout
            request.session.set_expiry(security_settings.session_timeout * 60)
            
            # Log activity
            UserActivityLog.objects.create(
                user=user,
                activity_type='security_settings_update',
                description='Security settings updated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Security settings updated successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
    except Exception as e:
        logger.error(f"Error updating security settings: {e}")
        messages.error(request, 'An error occurred while updating your security settings.')
    
    return redirect('profile')

@login_required
def change_password(request):
    """Change user password"""
    if request.method != 'POST':
        return redirect('profile')
    
    try:
        user = request.user
        form = CustomPasswordChangeForm(user, request.POST)
        
        if form.is_valid():
            form.save()
            
            # Update security settings
            security_settings, created = UserSecuritySettings.objects.get_or_create(user=user)
            security_settings.password_changed_at = timezone.now()
            security_settings.save()
            
            # Log activity
            UserActivityLog.objects.create(
                user=user,
                activity_type='password_change',
                description='Password changed successfully',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Password changed successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
                    
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        messages.error(request, 'An error occurred while changing your password.')
    
    return redirect('profile')

@login_required
def delete_account(request):
    """Delete user account"""
    if request.method != 'POST':
        return redirect('profile')
    
    try:
        # Check if user confirmed deletion
        if request.POST.get('confirm_deletion') != 'on':
            messages.error(request, 'You must confirm account deletion.')
            return redirect('profile')
        
        user = request.user
        reason = request.POST.get('reason', '')
        feedback = request.POST.get('feedback', '')
        
        # Log deletion request
        UserActivityLog.objects.create(
            user=user,
            activity_type='account_deletion',
            description=f'Account deletion requested: {reason} - {feedback}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"Account deletion requested for user {user.id}: {reason} - {feedback}")
        
        # Delete user (this will cascade to related profiles, preferences, and security settings)
        user.delete()
        
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('login')
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        messages.error(request, 'An error occurred while deleting your account.')
    
    return redirect('profile')


# ==================== DRIVER REGISTRATION WEB VIEWS ====================

def driver_registration(request):
    """Driver registration form view"""
    from rides.models import VehicleType
    
    if request.method == 'POST':
        # Handle form submission
        return JsonResponse({'message': 'Use API endpoint for registration'})
    
    vehicle_types = VehicleType.objects.all()
    context = {
        'vehicle_types': vehicle_types,
    }
    return render(request, 'accounts/driver_registration.html', context)


def driver_verification(request):
    """Driver verification page"""
    return render(request, 'accounts/driver_verification.html')


def driver_registration_dashboard(request):
    """Driver registration progress dashboard"""
    if not request.user.is_authenticated or not request.user.is_driver:
        return redirect('login')
    
    try:
        driver_profile = request.user.driver_profile
        
        # Get registration status
        completed_steps = []
        pending_steps = []
        
        if driver_profile.first_name and driver_profile.last_name:
            completed_steps.append('Basic Information')
        else:
            pending_steps.append('Basic Information')
        
        if driver_profile.email_confirmed:
            completed_steps.append('Email Verification')
        else:
            pending_steps.append('Email Verification')
        
        if driver_profile.is_verified:
            completed_steps.append('Phone Verification')
        else:
            pending_steps.append('Phone Verification')
        
        if driver_profile.photo:
            completed_steps.append('Profile Photo')
        else:
            pending_steps.append('Profile Photo')
        
        if driver_profile.vehicle:
            completed_steps.append('Vehicle Registration')
        else:
            pending_steps.append('Vehicle Registration')
        
        if driver_profile.is_active:
            completed_steps.append('Admin Approval')
        else:
            pending_steps.append('Admin Approval')
        
        context = {
            'driver_profile': driver_profile,
            'completed_steps': completed_steps,
            'pending_steps': pending_steps,
            'registration_complete': len(pending_steps) == 0
        }
        
        return render(request, 'accounts/driver_registration_dashboard.html', context)
        
    except DriverProfile.DoesNotExist:
        messages.error(request, 'Driver profile not found. Please complete registration.')
        return redirect('driver_registration')


def driver_profile_update(request):
    """Update driver profile information"""
    if not request.user.is_authenticated or not request.user.is_driver:
        return redirect('login')
    
    try:
        driver_profile = request.user.driver_profile
        
        if request.method == 'POST':
            # Update profile information
            driver_profile.first_name = request.POST.get('first_name', driver_profile.first_name)
            driver_profile.last_name = request.POST.get('last_name', driver_profile.last_name)
            driver_profile.other_name = request.POST.get('other_name', driver_profile.other_name)
            driver_profile.bio = request.POST.get('bio', driver_profile.bio)
            driver_profile.city = request.POST.get('city', driver_profile.city)
            driver_profile.country = request.POST.get('country', driver_profile.country)
            
            if 'photo' in request.FILES:
                driver_profile.photo = request.FILES['photo']
            
            if 'cover_photo' in request.FILES:
                driver_profile.cover_photo = request.FILES['cover_photo']
            
            driver_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('driver_profile_update')
        
        context = {
            'driver_profile': driver_profile,
        }
        return render(request, 'accounts/driver_profile_update.html', context)
        
    except DriverProfile.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('driver_registration')


def driver_vehicle_registration(request):
    """Driver vehicle registration page"""
    if not request.user.is_authenticated or not request.user.is_driver:
        return redirect('login')
    
    from rides.models import VehicleType
    
    try:
        driver_profile = request.user.driver_profile
        
        if request.method == 'POST':
            # Handle vehicle registration
            vehicle_type_id = request.POST.get('vehicle_type')
            vehicle_name = request.POST.get('vehicle_name')
            vehicle_registration = request.POST.get('vehicle_registration')
            vehicle_description = request.POST.get('vehicle_description', '')
            is_air_conditioned = request.POST.get('is_air_conditioned') == 'on'
            is_insured = request.POST.get('is_insured') == 'on'
            manufacturing_year = request.POST.get('manufacturing_year')
            
            if vehicle_type_id and vehicle_name and vehicle_registration:
                from rides.models import Vehicle, VehiclePhoto, VehicleDocument
                
                try:
                    vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
                    
                    # Create or update vehicle
                    if driver_profile.vehicle:
                        vehicle = driver_profile.vehicle
                        vehicle.name = vehicle_name
                        vehicle.registration_number = vehicle_registration
                        vehicle.description = vehicle_description
                        vehicle.is_air_conditioned = is_air_conditioned
                        vehicle.is_insured = is_insured
                        if manufacturing_year:
                            vehicle.manufacturing_year = manufacturing_year
                        vehicle.save()
                    else:
                        vehicle = Vehicle.objects.create(
                            type=vehicle_type,
                            name=vehicle_name,
                            registration_number=vehicle_registration,
                            description=vehicle_description,
                            is_air_conditioned=is_air_conditioned,
                            is_insured=is_insured,
                            manufacturing_year=manufacturing_year if manufacturing_year else None
                        )
                        driver_profile.vehicle = vehicle
                        driver_profile.save()
                    
                    # Handle vehicle photos
                    vehicle_photos = request.FILES.getlist('vehicle_photos', [])
                    for photo in vehicle_photos:
                        VehiclePhoto.objects.create(vehicle=vehicle, photo=photo)
                    
                    # Handle vehicle documents
                    vehicle_documents = request.FILES.getlist('vehicle_documents', [])
                    for document in vehicle_documents:
                        VehicleDocument.objects.create(vehicle=vehicle, file=document)
                    
                    messages.success(request, 'Vehicle registered successfully!')
                    return redirect('driver_vehicle_registration')
                    
                except VehicleType.DoesNotExist:
                    messages.error(request, 'Invalid vehicle type selected.')
                except Exception as e:
                    messages.error(request, f'Error registering vehicle: {str(e)}')
        
        vehicle_types = VehicleType.objects.all()
        context = {
            'driver_profile': driver_profile,
            'vehicle_types': vehicle_types,
            'vehicle': driver_profile.vehicle if hasattr(driver_profile, 'vehicle') else None
        }
        return render(request, 'accounts/driver_vehicle_registration.html', context)
        
    except DriverProfile.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('driver_registration')