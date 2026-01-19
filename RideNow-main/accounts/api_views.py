import logging
import traceback

from django.conf import settings
from django.db import transaction
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.models import ErrorLogs, OTP
from core.utils import send_email_alert, send_sms_alert
from core.tasks import send_email_task, send_sms_alert_task
from .models import (
    User, ClientProfile, DriverProfile, VerificationToken, 
    ReportUser, ReportEvidence, TermsAcceptance, UserPreferences, 
    UserSecuritySettings, UserActivityLog, UserSession
)

from .serializers import (
    ClientSignupSerializer, DriverSignupSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ClientProfileSerializer, DriverProfileSerializer, UserProfileSerializer,
    ChangePasswordSerializer, ReportUserSerializer, ReportEvidenceSerializer,
    AccountDeletionSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


def send_verification_token(user, token, email=None, phone=None):
    """Send verification token to user via email and SMS"""
    try:
        # Send email verification in background
        if email:
            send_email_task.delay(
                email=email,
                subject="Verify Your Zyra Account",
                message=(
                    f"Dear {user.get_user_names},\n\n"
                    f"Thank you for registering with Zyra. Your verification code is:\n\n"
                    f"{token}\n\n"
                    "Please enter this code in the verification page to activate your account.\n\n"
                    "If you did not request this verification, please ignore this message.\n\n"
                    "For support, contact us at support@zyracab.com or call +256789079301.\n\n"
                    "Best regards,\n"
                    "The Zyra Team"
                )
            )

        # Send SMS verification in background
        if phone:
            send_sms_alert_task.delay(
                body=f"Your Zyra verification code is: {token}",
                sms_phone=phone
            )

        if not email and not phone:
            raise Exception("Email or phone number is required")
        
    except Exception as e:
        ErrorLogs.objects.create(
            error_narration=f"Error sending verification: {str(e)}",
            traceback=traceback.format_exc()
        )


@extend_schema(
    summary="Client Registration",
    description="Register a new client account",
    tags=["Authentication"]
)
class ClientSignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ClientSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Create verification token
                    token_obj = VerificationToken.objects.create(
                        user=user, 
                        token_type='EMAIL_VERIFICATION'
                    )
                    
                    # Send verification token
                    send_verification_token(user, token_obj.token, email=user.email, phone=user.phone_number)
                    
                    return Response({
                        "message": "Client registration successful. Please verify your account.",
                        "user_id": user.id,
                        "email": user.email,
                        "phone": str(user.phone_number) if user.phone_number else None
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                ErrorLogs.objects.create(
                    error_narration=f"Error in client signup: {str(e)}",
                    traceback=traceback.format_exc()
                )
                return Response(
                    {"error": "Registration failed. Please try again. Error: " + str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Driver Registration",
    description="Register a new driver account",
    tags=["Authentication"]
)
class DriverSignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DriverSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Create verification token
                    token_obj = VerificationToken.objects.create(
                        user=user, 
                        token_type='EMAIL_VERIFICATION'
                    )
                    
                    # Send verification token
                    send_verification_token(user, token_obj.token, email=user.email, phone=user.phone_number)
                    
                    return Response({
                        "message": "Driver registration successful. Please verify your account.",
                        "user_id": user.id,
                        "email": user.email,
                        "phone": str(user.phone_number) if user.phone_number else None
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                ErrorLogs.objects.create(
                    error_narration=f"Error in driver signup: {str(e)}",
                    traceback=traceback.format_exc()
                )
                return Response(
                    {"error": "Registration failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="User Login",
    description="Authenticate user and return JWT tokens",
    tags=["Authentication"]
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        username_or_email_or_phone = serializer.validated_data['username_or_email_or_phone']
        password = serializer.validated_data['password']

        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email_or_phone, password=password)
        
        # If not found, try email or phone
        if user is None:
            try:
                if '@' in username_or_email_or_phone:
                    user = User.objects.get(email=username_or_email_or_phone)
                else:
                    user = User.objects.get(phone_number=username_or_email_or_phone)
                
                user = authenticate(request, username=user.username, password=password)
            except ObjectDoesNotExist:
                return Response(
                    {"detail": "Invalid credentials."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

        if user is not None:
            if not user.is_active:
                return Response(
                    {"detail": "Account is not active. Please verify your account."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Create Django session for traditional authentication
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Generate JWT tokens for API authentication
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_client': user.is_client,
                    'is_driver': user.is_driver
                },
                'redirect_url': '/rides/dashboard/' if user.is_client else '/rides/driver-dashboard/'
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"detail": "Invalid credentials."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    summary="Account Verification",
    description="Verify user account with verification token",
    tags=["Authentication"]
)
class VerifyAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('verification_code')
        if not token:
            return Response(
                {"error": "Verification code is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = VerificationToken.objects.get(
                token=token, 
                token_type='EMAIL_VERIFICATION'
            )
            if not verification.is_valid():
                return Response(
                    {"error": "Invalid or expired verification code."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except VerificationToken.DoesNotExist:
            return Response(
                {"error": "Invalid verification code."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate user and profile
        user = verification.user
        user.is_active = True
        user.save()
        
        # Update profile
        profile = user.get_user_profile()
        if profile:
            profile.is_active = True
            profile.is_verified = True
            profile.email_confirmed = True
            profile.save()
        
        verification.mark_as_used()

        # Login user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return Response({
            "message": "Account verified successfully.",
            "user_id": user.id
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Password Reset Request",
    description="Request password reset for user account",
    tags=["Authentication"]
)
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create password reset token
                reset_token = VerificationToken.objects.create(
                    user=user, 
                    token_type='PASSWORD_RESET'
                )
                
                # Send password reset email
                reset_url = f"{request.scheme}://{request.get_host()}/api/password-reset/confirm/?token={reset_token.token}"
                
                send_email_task.delay(
                    email=user.email,
                    subject="Reset Your Zyra Password",
                    message=(
                        f"Dear {user.get_user_names()},\n\n"
                        f"We received a request to reset your password for your Zyra account.\n\n"
                        f"To reset your password, please click the link below:\n\n"
                        f"{reset_url}\n\n"
                        f"This link will expire in 1 hour for security reasons.\n\n"
                        f"If you did not request this password reset, please ignore this email. "
                        f"Your password will remain unchanged.\n\n"
                        f"For support, contact us at support@ridenow.com or call +256789079301.\n\n"
                        f"Best regards,\n"
                        f"The Zyra Team"
                    )
                )
                
                return Response({
                    "message": "Password reset link has been sent to your email address."
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                return Response({
                    "message": "If an account with this email exists, a password reset link has been sent."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                ErrorLogs.objects.create(
                    error_narration=f"Error sending password reset email: {str(e)}",
                    traceback=traceback.format_exc()
                )
                return Response(
                    {"error": "Failed to send password reset email. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Password Reset Confirm",
    description="Confirm password reset with token",
    tags=["Authentication"]
)
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['new_password']
            
            try:
                # Update user password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.mark_as_used()
                
                # Send confirmation email in background
                send_email_task.delay(
                    email=user.email,
                    subject="Password Successfully Reset - Zyra",
                    message=(
                        f"Dear {user.get_user_names()},\n\n"
                        f"Your password has been successfully reset for your Zyra account.\n\n"
                        f"If you did not make this change, please contact our support team immediately at "
                        f"support@ridenow.com or call +256789079301.\n\n"
                        f"For security reasons, we recommend using a strong, unique password.\n\n"
                        f"Best regards,\n"
                        f"The Zyra Team"
                    )
                )
                
                return Response({
                    "message": "Password has been successfully reset. You can now log in with your new password."
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                ErrorLogs.objects.create(
                    error_narration=f"Error resetting password: {str(e)}",
                    traceback=traceback.format_exc()
                )
                return Response(
                    {"error": "Failed to reset password. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get User Profile",
    description="Get current user's profile information",
    tags=["Profile Management"]
)
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update Client Profile",
    description="Update client profile information",
    tags=["Profile Management"]
)
class UpdateClientProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_client:
            return Response(
                {"error": "User is not a client."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = request.user.client_profile
            serializer = ClientProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response(
                {"error": "Client profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        if not request.user.is_client:
            return Response(
                {"error": "User is not a client."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = request.user.client_profile
            serializer = ClientProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClientProfile.DoesNotExist:
            return Response(
                {"error": "Client profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="Update Driver Profile",
    description="Update driver profile information",
    tags=["Profile Management"]
)
class UpdateDriverProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_driver:
            return Response(
                {"error": "User is not a driver."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = request.user.driver_profile
            serializer = DriverProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "Driver profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        if not request.user.is_driver:
            return Response(
                {"error": "User is not a driver."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = request.user.driver_profile
            serializer = DriverProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DriverProfile.DoesNotExist:
            return Response(
                {"error": "Driver profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="Change Password",
    description="Change user password",
    tags=["Account Management"]
)
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verify old password
            if not request.user.check_password(old_password):
                return Response(
                    {"error": "Old password is incorrect."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            request.user.set_password(new_password)
            request.user.save()
            
            return Response({
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Report User",
    description="Report a user for inappropriate behavior",
    tags=["User Management"]
)
class ReportUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReportUserSerializer(data=request.data)
        
        if serializer.is_valid():
            report = serializer.save(reporter=request.user)
            return Response({
                "message": "User reported successfully.",
                "report_id": report.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Add Report Evidence",
    description="Add evidence to a user report",
    tags=["User Management"]
)
class AddReportEvidenceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        report_id = request.data.get('report_id')
        if not report_id:
            return Response(
                {"error": "Report ID is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            report = ReportUser.objects.get(id=report_id, reporter=request.user)
        except ReportUser.DoesNotExist:
            return Response(
                {"error": "Report not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ReportEvidenceSerializer(data=request.data)
        if serializer.is_valid():
            evidence = serializer.save(report=report)
            return Response({
                "message": "Evidence added successfully.",
                "evidence_id": evidence.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Delete Account",
    description="Permanently delete user account",
    tags=["Account Management"]
)
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AccountDeletionSerializer(data=request.data)
        
        if serializer.is_valid():
            password = serializer.validated_data['password']
            reason = serializer.validated_data.get('reason', '')
            feedback = serializer.validated_data.get('feedback', '')
            
            # Verify password
            if not request.user.check_password(password):
                return Response(
                    {"error": "Incorrect password."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                with transaction.atomic():
                    # Log deletion reason (optional - create model if needed)
                    # AccountDeletionLog.objects.create(
                    #     user_name=request.user.username,
                    #     reason=reason,
                    #     feedback=feedback
                    # )
                    
                    # Delete the user account
                    request.user.delete()
                    
                    return Response({
                        "message": "Account deleted successfully."
                    }, status=status.HTTP_200_OK)
                    
            except Exception as e:
                ErrorLogs.objects.create(
                    error_narration=f"Error deleting account: {str(e)}",
                    traceback=traceback.format_exc()
                )
                return Response(
                    {"error": "Failed to delete account. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Resend Verification",
    description="Resend verification token to user",
    tags=["Authentication"]
)
class ResendVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # if request.user.is_active:
        #     return Response(
        #         {"error": "Account is already verified."}, 
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        email = request.data.get('email') if request.data.get('email') else None
        phone = request.data.get('phone') if request.data.get('phone') else None

        try:
            user = User.objects.get(email=email) if email else User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Create new verification token
            token_obj = VerificationToken.objects.create(
                user=user, 
                token_type='EMAIL_VERIFICATION' if email else 'PHONE_VERIFICATION'
            )
            
            # Send verification token
            send_verification_token(user, token_obj.token, email, phone)
            
            return Response({
                "message": "Verification code has been resent to your email."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            ErrorLogs.objects.create(
                error_narration=f"Error resending verification: {str(e)}",
                traceback=traceback.format_exc()
            )
            return Response(
                {"error": "Failed to resend verification. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    summary="Logout",
    description="Logout user and blacklist refresh token",
    tags=["Authentication"]
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Logout failed."},
                status=status.HTTP_400_BAD_REQUEST
            )


# =============== QUICK AUTHENTICATION FOR RIDE BOOKING ===============

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def quick_login(request):
    """Quick login endpoint for ride booking modals"""
    from django.contrib.auth import login
    
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    
    if not phone_number or not password:
        return Response({
            'success': False,
            'error': 'Phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Authenticate user
        user = User.objects.filter(phone_number=phone_number).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return Response({
                    'success': False,
                    'error': 'Account is not active. Please verify your account.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone_number': str(user.phone_number),
                    'is_client': user.is_client,
                    'is_driver': user.is_driver
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Invalid phone number or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"Quick login error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Login failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def quick_signup(request):
    """Quick signup endpoint for ride booking modals"""
    from core.models import OTP
    
    full_name = request.data.get('full_name')
    email = request.data.get('email', '').strip() if request.data.get('email') else ''
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    user_type = request.data.get('user_type', 'client')
    
    if not all([full_name, phone_number, password]):
        return Response({
            'success': False,
            'error': 'Full name, phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if user already exists
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({
                'success': False,
                'error': 'An account with this phone number already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create username from phone number
        username = phone_number.replace('+', '').replace(' ', '')
        
        # Debug logging
        logger.info(f"Quick signup - Email received: '{email}', Type: {type(email)}")
        
        with transaction.atomic():
            # Generate a default email if not provided or empty
            if not email or email.strip() == '' or email == 'undefined':
                base_email = f"{username}@zyracab.com"
                email = base_email
                counter = 1
                # Ensure email is unique
                while User.objects.filter(email=email).exists():
                    email = f"{username}{counter}@zyracab.com"
                    counter += 1
                logger.info(f"Generated default email: {email}")
            else:
                logger.info(f"Using provided email: {email}")
            
            # Create user
            user = User.objects.create_user(
                email=email,
                phone_number=phone_number,
                username=username,
                password=password,
                is_active=False  # Require OTP verification
            )
            
            # Parse full name
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            
            # Set user type and create profile
            if user_type == 'client':
                user.is_client = True
                ClientProfile.objects.create(
                    user=user,
                    username=username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=email
                )
            elif user_type == 'driver':
                user.is_driver = True
                DriverProfile.objects.create(
                    user=user,
                    username=username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=email
                )
            
            user.save()
            
            # Generate and send OTP
            otp_obj = OTP.generate_otp(phone_number)
            
            # Send OTP via SMS
            sms_sent = False
            try:
                send_sms_alert_task.delay(
                    body=f"Your Zyra verification code is: {otp_obj.otp}. Valid for 10 minutes.",
                    sms_phone=phone_number
                )
                sms_sent = True
            except Exception as sms_error:
                logger.error(f"SMS sending failed: {str(sms_error)}")
                # Continue with signup even if SMS fails - user can still verify via other means
            
            response_data = {
                'success': True,
                'message': 'Account created successfully.' + (' OTP sent to your phone.' if sms_sent else ' Please contact support for verification.'),
                'user_id': user.id,
                'sms_sent': sms_sent
            }
            
            # In development/debug mode, include the OTP for testing
            if settings.DEBUG and not sms_sent:
                response_data['debug_otp'] = otp_obj.otp
                response_data['message'] += f' Debug OTP: {otp_obj.otp}'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Quick signup error: {str(e)}")
        return Response({
            'success': False,
            'error': f'Signup failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify OTP and activate user account"""
    print(f"Verify OTP request: {request.data}")

    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    otp_code = request.data.get('otp')
    
    print(f"Phone number: {phone_number}, Email: {email}, OTP code: {otp_code}")

    if not otp_code:
        return Response({
            'success': False,
            'error': 'OTP code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not phone_number and not email:
        return Response({
            'success': False,
            'error': 'Phone number or email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get the latest OTP for this phone number
        if email:
            otp_obj = OTP.objects.filter(
                email=email,
                is_active=True,
                is_verified=False
            ).order_by('-created_at').first()
        else:
            otp_obj = OTP.objects.filter(
                phone_number=phone_number,
                is_active=True,
                is_verified=False
            ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response({
                'success': False,
                'error': 'No active OTP found. Please request a new one.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP
        if otp_obj.verify(otp_code):
            # Activate user account
            if email:
                user = User.objects.filter(email=email).first()
            else:
                user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.is_active = True
                user.save()
                
                # Login user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                return Response({
                    'success': True,
                    'message': 'Phone number verified successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'is_client': user.is_client
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'error': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Verification failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_otp(request):
    """Resend OTP to phone number"""
    from core.models import OTP
    
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if user exists
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'success': False,
                'error': 'No account found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new OTP
        otp_obj = OTP.generate_otp(phone_number)
        
        # Send OTP via SMS
        send_sms_alert_task.delay(
            body=f"Your Zyra verification code is: {otp_obj.otp}. Valid for 10 minutes.",
            sms_phone=phone_number
        )
        
        return Response({
            'success': True,
            'message': 'New OTP sent to your phone'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Resend OTP error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== PASSWORD RESET ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """Request password reset via OTP"""
    from core.models import OTP
    
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check if user exists
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'success': False,
                'error': 'No account found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP for password reset
        otp_obj = OTP.generate_otp(phone_number)
        
        # Send OTP via SMS
        send_sms_alert_task.delay(
            body=f"Your Zyra password reset code is: {otp_obj.otp}. Valid for 10 minutes.",
            sms_phone=phone_number
        )

        send_email_task.delay(
            email=user.email,
            subject="Password Reset Code",
            message=f"Your Zyra password reset code is: {otp_obj.otp}. Valid for 10 minutes."
        )
        
        return Response({
            'success': True,
            'message': 'Reset code sent to your phone'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send reset code. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with OTP and new password"""
    from core.models import OTP
    
    phone_number = request.data.get('phone_number')
    otp_code = request.data.get('otp')
    new_password = request.data.get('new_password')
    
    if not all([phone_number, otp_code, new_password]):
        return Response({
            'success': False,
            'error': 'Phone number, OTP, and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get the latest OTP
        otp_obj = OTP.objects.filter(
            phone_number=phone_number,
            is_active=True,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response({
                'success': False,
                'error': 'No active reset code found. Please request a new one.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP
        if otp_obj.verify(otp_code):
            # Reset password
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Password reset successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'error': 'Invalid or expired reset code'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Password reset failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== PROFILE MANAGEMENT ====================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_client_profile_quick(request):
    """Quick update client profile for new users"""
    try:
        user = request.user
        
        # Update user basic info
        if request.data.get('first_name'):
            user.first_name = request.data.get('first_name')
        if request.data.get('last_name'):
            user.last_name = request.data.get('last_name')
        if request.data.get('email'):
            user.email = request.data.get('email')
        
        user.save()
        
        # Update or create client profile
        client_profile, created = ClientProfile.objects.get_or_create(user=user)
        
        if request.data.get('date_of_birth'):
            client_profile.date_of_birth = request.data.get('date_of_birth')
        if request.data.get('gender'):
            # Validate and normalize gender value
            gender = request.data.get('gender')
            if gender.lower() in ['male', 'm']:
                client_profile.gender = 'M'
            elif gender.lower() in ['female', 'f']:
                client_profile.gender = 'F'
            else:
                client_profile.gender = gender  # Assume it's already 'M' or 'F'
        if request.data.get('address'):
            # Map address to city field since there's no address field in the model
            client_profile.city = request.data.get('address')
        
        # Handle profile photo if provided
        if request.FILES.get('profile_photo'):
            client_profile.profile_photo = request.FILES.get('profile_photo')
        
        client_profile.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to update profile. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_profile_completeness(request):
    """Check if user profile is complete for ride booking"""
    try:
        user = request.user
        
        # Define required fields for ride booking
        required_fields = {
            'user': ['first_name', 'last_name', 'email', 'phone_number'],
            'client_profile': ['date_of_birth', 'gender', 'city']
        }
        
        missing_fields = []
        is_complete = True
        
        # Check user fields
        for field in required_fields['user']:
            value = getattr(user, field, None)
            if not value or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field.replace('_', ' ').title())
                is_complete = False
        
        # Check client profile fields if user is a client
        if user.is_client:
            try:
                profile = user.client_profile
                for field in required_fields['client_profile']:
                    value = getattr(profile, field, None)
                    if not value or (isinstance(value, str) and value.strip() == ''):
                        missing_fields.append(field.replace('_', ' ').title())
                        is_complete = False
            except ClientProfile.DoesNotExist:
                missing_fields.extend([field.replace('_', ' ').title() for field in required_fields['client_profile']])
                is_complete = False
        
        # Calculate completion percentage
        total_fields = len(required_fields['user']) + (len(required_fields['client_profile']) if user.is_client else 0)
        completed_fields = total_fields - len(missing_fields)
        completion_percentage = round((completed_fields / total_fields) * 100) if total_fields > 0 else 0
        
        return Response({
            'is_complete': is_complete,
            'completion_percentage': completion_percentage,
            'missing_fields': missing_fields,
            'total_fields': total_fields,
            'completed_fields': completed_fields
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile completeness check error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to check profile completeness'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_terms_acceptance(request):
    """Check if user has accepted Terms of Service"""
    try:
        user = request.user
        has_accepted = hasattr(user, 'terms_acceptance')
        
        return Response({
            'has_accepted_terms': has_accepted,
            'accepted_at': user.terms_acceptance.accepted_at.isoformat() if has_accepted else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Terms acceptance check error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to check terms acceptance'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_terms_of_service(request):
    """Accept Terms of Service"""
    try:
        from .models import TermsAcceptance
        
        user = request.user
        
        # Debug logging for production issues
        logger.info(f"Terms acceptance request from user {user.id}: {request.META.get('REMOTE_ADDR')}")
        
        # Check if user has already accepted
        if hasattr(user, 'terms_acceptance'):
            return Response({
                'success': True,
                'message': 'Terms of Service already accepted',
                'accepted_at': user.terms_acceptance.accepted_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        # Create terms acceptance record
        terms_acceptance = TermsAcceptance.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            terms_version=request.data.get('terms_version', '1.0')
        )
        
        return Response({
            'success': True,
            'message': 'Terms of Service accepted successfully',
            'accepted_at': terms_acceptance.accepted_at.isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Terms acceptance error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to accept Terms of Service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== DRIVER REGISTRATION APIs ====================

@extend_schema(
    summary="Complete Driver Registration",
    description="Complete driver registration with profile, vehicle, and document information",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Unique username'},
                'first_name': {'type': 'string', 'description': 'Driver first name'},
                'last_name': {'type': 'string', 'description': 'Driver last name'},
                'email': {'type': 'string', 'format': 'email', 'description': 'Driver email'},
                'phone': {'type': 'string', 'description': 'Phone number with country code'},
                'country': {'type': 'string', 'description': 'Country code (e.g., UG)'},
                'city': {'type': 'string', 'description': 'City'},
                'gender': {'type': 'string', 'enum': ['M', 'F'], 'description': 'Gender'},
                'date_of_birth': {'type': 'string', 'format': 'date', 'description': 'Date of birth'},
                'bio': {'type': 'string', 'description': 'Driver bio'},
                'vehicle_registration': {'type': 'string', 'description': 'Vehicle registration number'},
                'drivers_license_no': {'type': 'string', 'description': 'Driver license number'},
                'photo': {'type': 'string', 'format': 'binary', 'description': 'Driver portrait photo'},
                'cover_photo': {'type': 'string', 'format': 'binary', 'description': 'Cover photo'},
                'vehicle_type_id': {'type': 'integer', 'description': 'Vehicle type ID'},
                'vehicle_name': {'type': 'string', 'description': 'Vehicle name'},
                'vehicle_description': {'type': 'string', 'description': 'Vehicle description'},
                'is_air_conditioned': {'type': 'boolean', 'description': 'Has air conditioning'},
                'is_insured': {'type': 'boolean', 'description': 'Is insured'},
                'manufacturing_year': {'type': 'string', 'format': 'date', 'description': 'Vehicle manufacturing year'},
                'vehicle_photos': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}, 'description': 'Vehicle photos'},
                'vehicle_documents': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}, 'description': 'Vehicle documents'},
                'terms_accepted': {'type': 'boolean', 'description': 'Terms of service acceptance'},
                'ip_address': {'type': 'string', 'description': 'User IP address'},
                'user_agent': {'type': 'string', 'description': 'User agent string'}
            },
            'required': ['username', 'first_name', 'last_name', 'email', 'phone', 'vehicle_registration', 'vehicle_type_id', 'vehicle_name', 'terms_accepted']
        }
    },
    responses={
        201: {
            'description': 'Driver registered successfully',
            'content': {
                'application/json': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string'},
                        'user_id': {'type': 'integer'},
                        'profile_id': {'type': 'integer'},
                        'verification_required': {'type': 'boolean'},
                        'next_steps': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            }
        },
        400: {'description': 'Validation errors'},
        500: {'description': 'Server error'}
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def complete_driver_registration(request):
    """
    Complete driver registration with all required information
    """
    try:
        # Access data directly without copying to avoid pickle issues with file uploads
        data = request.data
        
        # Validate required fields
        required_fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'vehicle_registration', 'vehicle_type_id', 'vehicle_name', 'terms_accepted']
        
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'error': f'{field} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=data['email']).exists():
            return Response({
                'success': False,
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=data['username']).exists():
            return Response({
                'success': False,
                'error': 'Username already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if phone number already exists
        if User.objects.filter(phone_number=data['phone']).exists():
            return Response({
                'success': False,
                'error': 'Phone number already registered. Please use a different number or try logging in.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if driver profile username exists
        if DriverProfile.objects.filter(username=data['username']).exists():
            return Response({
                'success': False,
                'error': 'Username already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if vehicle registration exists
        if DriverProfile.objects.filter(vehicle_registration=data['vehicle_registration']).exists():
            return Response({
                'success': False,
                'error': 'Vehicle registration number already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create user account
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data.get('password', 'temp_password_123'),  # Will be set during verification
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone'],
                is_driver=True
            )
            
            # Create driver profile
            driver_profile = DriverProfile.objects.create(
                user=user,
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                other_name=data.get('other_name'),
                email=data['email'],
                phone=data['phone'],
                country=data.get('country', 'UG'),
                city=data.get('city', 'Kampala'),
                gender=data.get('gender'),
                date_of_birth=data.get('date_of_birth'),
                bio=data.get('bio'),
                vehicle_registration=data['vehicle_registration'],
                drivers_license_no=data.get('drivers_license_no'),
                photo=request.FILES.get('photo'),
                cover_photo=request.FILES.get('cover_photo'),
                is_active=False,  # Will be activated after verification
                is_verified=False
            )
            
            # Create vehicle if vehicle type is provided
            from rides.models import VehicleType, Vehicle, VehiclePhoto, VehicleDocument
            
            try:
                vehicle_type = VehicleType.objects.get(id=data['vehicle_type_id'])
                
                # Parse manufacturing year if provided
                manufacturing_year = None
                if data.get('manufacturing_year'):
                    try:
                        from datetime import datetime
                        manufacturing_year = datetime.strptime(data['manufacturing_year'], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Invalid date format, will be None
                
                # Convert checkbox values to boolean
                # HTML checkboxes send 'on' when checked, nothing when unchecked
                is_air_conditioned = data.get('is_air_conditioned') == 'on' or data.get('is_air_conditioned') is True
                is_insured = data.get('is_insured') == 'on' or data.get('is_insured') is True
                
                logger.info(f"Vehicle creation - is_air_conditioned: {is_air_conditioned}, is_insured: {is_insured}")
                
                try:
                    vehicle = Vehicle.objects.create(
                        type=vehicle_type,
                        name=data['vehicle_name'],
                        registration_number=data['vehicle_registration'],
                        description=data.get('vehicle_description', ''),
                        is_air_conditioned=is_air_conditioned,
                        is_insured=is_insured,
                        manufacturing_year=manufacturing_year
                    )
                except Exception as ve:
                    logger.error(f"Vehicle creation error: {str(ve)}")
                    return Response({
                        'success': False,
                        'error': f'Vehicle creation failed: {str(ve)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Link vehicle to driver profile
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
                
            except VehicleType.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid vehicle type ID'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Record terms acceptance
            if data.get('terms_accepted'):
                TermsAcceptance.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    terms_version='1.0'
                )
            
            # Create verification token for email
            email_token = VerificationToken.objects.create(
                user=user,
                token_type='EMAIL_VERIFICATION'
            )
            
            # Send verification email using existing function
            try:
                send_verification_token(user, email_token.token)
            except Exception as e:
                logger.error(f"Failed to send verification token: {str(e)}")
            
            return Response({
                'success': True,
                'message': 'Driver registration completed successfully. Please verify your email and phone number.',
                'user_id': user.id,
                'profile_id': driver_profile.id,
                'verification_required': True,
                'next_steps': [
                    'Check your email for verification code',
                    'Verify your phone number',
                    'Complete profile verification',
                    'Wait for admin approval'
                ]
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Driver registration error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Handle specific database integrity errors
        if 'duplicate key value violates unique constraint' in str(e):
            if 'phone_number' in str(e):
                return Response({
                    'success': False,
                    'error': 'Phone number already registered. Please use a different number or try logging in.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in str(e):
                return Response({
                    'success': False,
                    'error': 'Email address already registered. Please use a different email or try logging in.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'username' in str(e):
                return Response({
                    'success': False,
                    'error': 'Username already taken. Please choose a different username.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Note: Using existing verification infrastructure
# Email verification: Use existing VerificationToken system
# Phone verification: Use existing OTP system


@extend_schema(
    summary="Get Driver Registration Status",
    description="Get driver registration completion status",
    responses={
        200: {
            'description': 'Registration status',
            'content': {
                'application/json': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'status': {'type': 'string'},
                        'completed_steps': {'type': 'array', 'items': {'type': 'string'}},
                        'pending_steps': {'type': 'array', 'items': {'type': 'string'}},
                        'profile': {'type': 'object'}
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_driver_registration_status(request):
    """Get driver registration completion status"""
    try:
        if not request.user.is_driver:
            return Response({
                'success': False,
                'error': 'User is not a driver'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            driver_profile = request.user.driver_profile
        except DriverProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Driver profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        completed_steps = []
        pending_steps = []
        
        # Check registration steps
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
        
        # Determine overall status
        if len(pending_steps) == 0:
            status_text = 'Completed'
        elif len(completed_steps) == 0:
            status_text = 'Not Started'
        else:
            status_text = 'In Progress'
        
        return Response({
            'success': True,
            'status': status_text,
            'completed_steps': completed_steps,
            'pending_steps': pending_steps,
            'profile': {
                'id': driver_profile.id,
                'username': driver_profile.username,
                'first_name': driver_profile.first_name,
                'last_name': driver_profile.last_name,
                'email': driver_profile.email,
                'email_confirmed': driver_profile.email_confirmed,
                'phone': str(driver_profile.phone) if driver_profile.phone else None,
                'is_verified': driver_profile.is_verified,
                'is_active': driver_profile.is_active,
                'has_photo': bool(driver_profile.photo),
                'has_vehicle': bool(driver_profile.vehicle),
                'vehicle_registration': driver_profile.vehicle_registration
            }
        })
        
    except Exception as e:
        logger.error(f"Registration status error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get registration status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== USER PREFERENCES & SECURITY SETTINGS APIs ====================

@extend_schema(
    summary="Get User Preferences",
    description="Get current user's preferences and settings",
    tags=["User Preferences"]
)
class UserPreferencesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user preferences"""
        try:
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            
            return Response({
                'success': True,
                'preferences': {
                    'email_notifications': preferences.email_notifications,
                    'sms_notifications': preferences.sms_notifications,
                    'push_notifications': preferences.push_notifications,
                    'marketing_emails': preferences.marketing_emails,
                    'profile_visibility': preferences.profile_visibility,
                    'language': preferences.language,
                    'timezone': preferences.timezone,
                    'preferred_payment_method': preferences.preferred_payment_method,
                    'auto_accept_rides': preferences.auto_accept_rides,
                    'max_ride_distance': preferences.max_ride_distance,
                    'preferred_ride_types': preferences.preferred_ride_types,
                    'preferred_driver_rating': float(preferences.preferred_driver_rating),
                    'preferred_vehicle_type': preferences.preferred_vehicle_type,
                    'created_at': preferences.created_at,
                    'updated_at': preferences.updated_at
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get preferences error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """Update user preferences"""
        try:
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            
            # Update preferences from request data
            update_fields = [
                'email_notifications', 'sms_notifications', 'push_notifications', 
                'marketing_emails', 'profile_visibility', 'language', 'timezone',
                'preferred_payment_method', 'auto_accept_rides', 'max_ride_distance',
                'preferred_ride_types', 'preferred_driver_rating', 'preferred_vehicle_type'
            ]
            
            for field in update_fields:
                if field in request.data:
                    setattr(preferences, field, request.data[field])
            
            preferences.save()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='preferences_update',
                description='User preferences updated via API',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'success': True,
                'message': 'Preferences updated successfully',
                'preferences': {
                    'email_notifications': preferences.email_notifications,
                    'sms_notifications': preferences.sms_notifications,
                    'push_notifications': preferences.push_notifications,
                    'marketing_emails': preferences.marketing_emails,
                    'profile_visibility': preferences.profile_visibility,
                    'language': preferences.language,
                    'timezone': preferences.timezone,
                    'preferred_payment_method': preferences.preferred_payment_method,
                    'auto_accept_rides': preferences.auto_accept_rides,
                    'max_ride_distance': preferences.max_ride_distance,
                    'preferred_ride_types': preferences.preferred_ride_types,
                    'preferred_driver_rating': float(preferences.preferred_driver_rating),
                    'preferred_vehicle_type': preferences.preferred_vehicle_type,
                    'updated_at': preferences.updated_at
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Update preferences error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to update preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get User Security Settings",
    description="Get current user's security settings",
    tags=["Security Settings"]
)
class UserSecuritySettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user security settings"""
        try:
            security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
            
            return Response({
                'success': True,
                'security_settings': {
                    'two_factor_enabled': security_settings.two_factor_enabled,
                    'login_alerts': security_settings.login_alerts,
                    'session_timeout': security_settings.session_timeout,
                    'max_concurrent_sessions': security_settings.max_concurrent_sessions,
                    'password_changed_at': security_settings.password_changed_at,
                    'password_expires_at': security_settings.password_expires_at,
                    'require_password_change': security_settings.require_password_change,
                    'account_locked': security_settings.account_locked,
                    'account_locked_until': security_settings.account_locked_until,
                    'failed_login_attempts': security_settings.failed_login_attempts,
                    'last_failed_login': security_settings.last_failed_login,
                    'data_sharing_consent': security_settings.data_sharing_consent,
                    'analytics_consent': security_settings.analytics_consent,
                    'location_tracking': security_settings.location_tracking,
                    'api_access_enabled': security_settings.api_access_enabled,
                    'api_key': security_settings.api_key,
                    'api_key_created_at': security_settings.api_key_created_at,
                    'created_at': security_settings.created_at,
                    'updated_at': security_settings.updated_at
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get security settings error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get security settings'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """Update user security settings"""
        try:
            security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
            
            # Update security settings from request data
            update_fields = [
                'two_factor_enabled', 'login_alerts', 'session_timeout', 
                'max_concurrent_sessions', 'data_sharing_consent', 
                'analytics_consent', 'location_tracking', 'api_access_enabled'
            ]
            
            for field in update_fields:
                if field in request.data:
                    setattr(security_settings, field, request.data[field])
            
            security_settings.save()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='security_settings_update',
                description='Security settings updated via API',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'success': True,
                'message': 'Security settings updated successfully',
                'security_settings': {
                    'two_factor_enabled': security_settings.two_factor_enabled,
                    'login_alerts': security_settings.login_alerts,
                    'session_timeout': security_settings.session_timeout,
                    'max_concurrent_sessions': security_settings.max_concurrent_sessions,
                    'data_sharing_consent': security_settings.data_sharing_consent,
                    'analytics_consent': security_settings.analytics_consent,
                    'location_tracking': security_settings.location_tracking,
                    'api_access_enabled': security_settings.api_access_enabled,
                    'updated_at': security_settings.updated_at
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Update security settings error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to update security settings'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Generate API Key",
    description="Generate a new API key for the user",
    tags=["Security Settings"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_api_key(request):
    """Generate a new API key for the user"""
    try:
        security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
        
        # Generate new API key
        api_key = security_settings.generate_api_key()
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='security_settings_update',
            description='API key generated',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'success': True,
            'message': 'API key generated successfully',
            'api_key': api_key,
            'created_at': security_settings.api_key_created_at
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Generate API key error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to generate API key'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Revoke API Key",
    description="Revoke the user's API key",
    tags=["Security Settings"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_api_key(request):
    """Revoke the user's API key"""
    try:
        security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
        
        # Revoke API key
        security_settings.revoke_api_key()
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='security_settings_update',
            description='API key revoked',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'success': True,
            'message': 'API key revoked successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Revoke API key error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to revoke API key'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get User Activity Logs",
    description="Get user's activity logs for security and audit purposes",
    tags=["Security Settings"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_activity_logs(request):
    """Get user's activity logs"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        activity_type = request.GET.get('activity_type')
        
        # Build queryset
        logs = UserActivityLog.objects.filter(user=request.user)
        
        if activity_type:
            logs = logs.filter(activity_type=activity_type)
        
        # Order by most recent first
        logs = logs.order_by('-created_at')
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_logs = logs[start:end]
        
        # Serialize logs
        logs_data = []
        for log in paginated_logs:
            logs_data.append({
                'id': log.id,
                'activity_type': log.activity_type,
                'activity_type_display': log.get_activity_type_display(),
                'description': log.description,
                'ip_address': log.ip_address,
                'location': log.location,
                'device_info': log.device_info,
                'created_at': log.created_at
            })
        
        return Response({
            'success': True,
            'logs': logs_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': logs.count(),
                'has_next': end < logs.count(),
                'has_previous': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get activity logs error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get activity logs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get User Sessions",
    description="Get user's active sessions",
    tags=["Security Settings"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_sessions(request):
    """Get user's active sessions"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        # Build queryset
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        
        # Order by most recent activity first
        sessions = sessions.order_by('-last_activity')
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_sessions = sessions[start:end]
        
        # Serialize sessions
        sessions_data = []
        for session in paginated_sessions:
            sessions_data.append({
                'id': session.id,
                'session_key': session.session_key[:8] + '...',  # Truncate for security
                'ip_address': session.ip_address,
                'location': session.location,
                'device_info': session.device_info,
                'is_active': session.is_active,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'expires_at': session.expires_at,
                'is_expired': session.is_expired()
            })
        
        return Response({
            'success': True,
            'sessions': sessions_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': sessions.count(),
                'has_next': end < sessions.count(),
                'has_previous': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get user sessions error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get user sessions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Terminate User Session",
    description="Terminate a specific user session",
    tags=["Security Settings"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_user_session(request):
    """Terminate a specific user session"""
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({
                'success': False,
                'error': 'Session ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = UserSession.objects.get(id=session_id, user=request.user)
            session.is_active = False
            session.save()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='security_settings_update',
                description=f'Session terminated: {session.session_key[:8]}...',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'success': True,
                'message': 'Session terminated successfully'
            }, status=status.HTTP_200_OK)
            
        except UserSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Terminate session error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to terminate session'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Terminate All Other Sessions",
    description="Terminate all user sessions except the current one",
    tags=["Security Settings"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_all_other_sessions(request):
    """Terminate all user sessions except the current one"""
    try:
        # Get current session key from request
        current_session_key = request.session.session_key
        
        # Terminate all other sessions
        terminated_count = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(
            session_key=current_session_key
        ).update(is_active=False)
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='security_settings_update',
            description=f'Terminated {terminated_count} other sessions',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'success': True,
            'message': f'Terminated {terminated_count} other sessions successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Terminate all sessions error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to terminate sessions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Update Password with Security Tracking",
    description="Update user password with security settings tracking",
    tags=["Security Settings"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_password_with_security(request):
    """Update user password with security settings tracking"""
    try:
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'success': False,
                'error': 'Old password and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify old password
        if not request.user.check_password(old_password):
            # Increment failed login attempts
            security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
            security_settings.increment_failed_login()
            
            return Response({
                'success': False,
                'error': 'Old password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update security settings
        security_settings, created = UserSecuritySettings.objects.get_or_create(user=request.user)
        security_settings.password_changed_at = timezone.now()
        security_settings.reset_failed_login()  # Reset failed attempts on successful password change
        security_settings.save()
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='password_change',
            description='Password changed via API',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'success': True,
            'message': 'Password updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Update password error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to update password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== SOCIAL LOGIN APIs ====================

@extend_schema(
    summary="Google Social Login",
    description="Authenticate user with Google OAuth and return JWT tokens",
    tags=["Social Authentication"]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_social_login(request):
    """Handle Google social login via API"""
    try:
        from allauth.socialaccount.models import SocialAccount
        from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
        from allauth.socialaccount.providers.oauth2.client import OAuth2Client
        from allauth.socialaccount.helpers import complete_social_login
        from allauth.socialaccount import app_settings
        
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({
                'success': False,
                'error': 'Google access token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a mock request for allauth
        from django.test import RequestFactory
        factory = RequestFactory()
        mock_request = factory.post('/')
        mock_request.session = request.session
        mock_request.user = request.user
        
        # Verify the Google token and get user info
        import requests
        google_user_info_url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        response = requests.get(google_user_info_url)
        
        if response.status_code != 200:
            return Response({
                'success': False,
                'error': 'Invalid Google access token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user_info = response.json()
        email = user_info.get('email')
        google_id = user_info.get('id')
        
        if not email or not google_id:
            return Response({
                'success': False,
                'error': 'Invalid Google user information'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                username=email.split('@')[0],
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_active=True,
                is_client=True
            )
            
            # Create client profile
            ClientProfile.objects.create(
                user=user,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=email,
                is_verified=True,
                is_active=True
            )
            
            # Create preferences and security settings
            UserPreferences.objects.get_or_create(user=user)
            UserSecuritySettings.objects.get_or_create(user=user)
        
        # Create or update social account
        social_account, created = SocialAccount.objects.get_or_create(
            provider='google',
            uid=google_id,
            defaults={
                'user': user,
                'extra_data': user_info
            }
        )
        
        if not created:
            social_account.extra_data = user_info
            social_account.save()
        
        # Create Django session
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='login',
            description='Google social login via API',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_info={
                'provider': 'google',
                'social_id': google_id,
                'profile_picture': user_info.get('picture', '')
            }
        )
        
        return Response({
            'success': True,
            'message': 'Google login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_client': user.is_client,
                'is_driver': user.is_driver,
                'profile_picture': user_info.get('picture', '')
            },
            'redirect_url': '/rides/dashboard/' if user.is_client else '/rides/driver-dashboard/'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Google social login error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Google login failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Apple Social Login",
    description="Authenticate user with Apple Sign In and return JWT tokens",
    tags=["Social Authentication"]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def apple_social_login(request):
    """Handle Apple social login via API"""
    try:
        from allauth.socialaccount.models import SocialAccount
        import jwt
        import requests
        
        identity_token = request.data.get('identity_token')
        authorization_code = request.data.get('authorization_code')
        user_info = request.data.get('user', {})
        
        if not identity_token:
            return Response({
                'success': False,
                'error': 'Apple identity token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode the identity token (without verification for now)
        # In production, you should verify the token with Apple's public keys
        try:
            decoded_token = jwt.decode(identity_token, options={"verify_signature": False})
        except jwt.DecodeError:
            return Response({
                'success': False,
                'error': 'Invalid Apple identity token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        email = decoded_token.get('email')
        apple_id = decoded_token.get('sub')
        
        if not email or not apple_id:
            return Response({
                'success': False,
                'error': 'Invalid Apple user information'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract name from user_info if available
        first_name = ''
        last_name = ''
        if user_info:
            name_data = user_info.get('name', {})
            first_name = name_data.get('firstName', '') if name_data else ''
            last_name = name_data.get('lastName', '') if name_data else ''
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                username=email.split('@')[0],
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_client=True
            )
            
            # Create client profile
            ClientProfile.objects.create(
                user=user,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=email,
                is_verified=True,
                is_active=True
            )
            
            # Create preferences and security settings
            UserPreferences.objects.get_or_create(user=user)
            UserSecuritySettings.objects.get_or_create(user=user)
        
        # Create or update social account
        social_account, created = SocialAccount.objects.get_or_create(
            provider='apple',
            uid=apple_id,
            defaults={
                'user': user,
                'extra_data': {
                    'email': email,
                    'name': {
                        'firstName': first_name,
                        'lastName': last_name
                    }
                }
            }
        )
        
        if not created:
            social_account.extra_data = {
                'email': email,
                'name': {
                    'firstName': first_name,
                    'lastName': last_name
                }
            }
            social_account.save()
        
        # Create Django session
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='login',
            description='Apple social login via API',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_info={
                'provider': 'apple',
                'social_id': apple_id
            }
        )
        
        return Response({
            'success': True,
            'message': 'Apple login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_client': user.is_client,
                'is_driver': user.is_driver
            },
            'redirect_url': '/rides/dashboard/' if user.is_client else '/rides/driver-dashboard/'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Apple social login error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Apple login failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get Social Login URLs",
    description="Get OAuth URLs for social login providers",
    tags=["Social Authentication"]
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_social_login_urls(request):
    """Get OAuth URLs for social login providers"""
    try:
        from django.urls import reverse
        from django.conf import settings
        
        base_url = request.build_absolute_uri('/')
        
        urls = {
            'google': {
                'auth_url': f"{base_url}accounts/google/login/",
                'callback_url': f"{base_url}accounts/google/login/callback/",
                'client_id': settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {}).get('client_id', ''),
                'scope': 'profile email'
            },
            'apple': {
                'auth_url': f"{base_url}accounts/apple/login/",
                'callback_url': f"{base_url}accounts/apple/login/callback/",
                'client_id': settings.SOCIALACCOUNT_PROVIDERS.get('apple', {}).get('APP', {}).get('client_id', ''),
                'scope': 'name email'
            }
        }
        
        return Response({
            'success': True,
            'urls': urls
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get social login URLs error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get social login URLs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Disconnect Social Account",
    description="Disconnect a social account from user profile",
    tags=["Social Authentication"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_social_account(request):
    """Disconnect a social account from user profile"""
    try:
        from allauth.socialaccount.models import SocialAccount
        
        provider = request.data.get('provider')
        if not provider:
            return Response({
                'success': False,
                'error': 'Provider is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            social_account = SocialAccount.objects.get(
                user=request.user,
                provider=provider
            )
            social_account.delete()
            
            # Log activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='security_settings_update',
                description=f'Disconnected {provider} social account',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'success': True,
                'message': f'{provider.title()} account disconnected successfully'
            }, status=status.HTTP_200_OK)
            
        except SocialAccount.DoesNotExist:
            return Response({
                'success': False,
                'error': f'{provider.title()} account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Disconnect social account error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to disconnect social account'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get Connected Social Accounts",
    description="Get list of connected social accounts for user",
    tags=["Social Authentication"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_connected_social_accounts(request):
    """Get list of connected social accounts for user"""
    try:
        from allauth.socialaccount.models import SocialAccount
        
        social_accounts = SocialAccount.objects.filter(user=request.user)
        
        accounts_data = []
        for account in social_accounts:
            accounts_data.append({
                'id': account.id,
                'provider': account.provider,
                'provider_display': account.get_provider().name,
                'uid': account.uid,
                'date_joined': account.date_joined,
                'extra_data': account.extra_data
            })
        
        return Response({
            'success': True,
            'accounts': accounts_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get connected social accounts error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get connected social accounts'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
