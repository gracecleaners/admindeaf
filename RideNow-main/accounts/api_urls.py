from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router for API views
router = DefaultRouter()

# API URL patterns
api_urlpatterns = [
    # Authentication endpoints
    path('auth/client/signup/', api_views.ClientSignupView.as_view(), name='client_signup'),
    path('auth/driver/signup/', api_views.DriverSignupView.as_view(), name='driver_signup'),
    path('auth/login/', api_views.LoginView.as_view(), name='login'),
    path('auth/logout/', api_views.LogoutView.as_view(), name='logout'),
    path('auth/verify/', api_views.VerifyAccountView.as_view(), name='verify_account'),
    path('auth/resend-verification/', api_views.ResendVerificationView.as_view(), name='resend_verification'),
    path('auth/verify-account/', api_views.VerifyAccountView.as_view(), name='verify_account'),
    
    # Password management
    path('auth/password-reset/request/', api_views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', api_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Profile management
    path('profile/', api_views.UserProfileView.as_view(), name='user_profile'),
    path('profile/client/', api_views.UpdateClientProfileView.as_view(), name='client_profile'),
    path('profile/driver/', api_views.UpdateDriverProfileView.as_view(), name='driver_profile'),
    
    # Account management
    path('account/change-password/', api_views.ChangePasswordView.as_view(), name='change_password'),
    path('account/delete/', api_views.DeleteAccountView.as_view(), name='delete_account'),
    
    # User reporting
    path('report/user/', api_views.ReportUserView.as_view(), name='report_user'),
    path('report/evidence/', api_views.AddReportEvidenceView.as_view(), name='add_report_evidence'),
    
    # Quick authentication for ride booking
    path('login/', api_views.quick_login, name='quick_login'),
    path('signup/', api_views.quick_signup, name='quick_signup'),
    path('verify-otp/', api_views.verify_otp, name='verify_otp'),
    path('resend-otp/', api_views.resend_otp, name='resend_otp'),
    path('password-reset/request/', api_views.password_reset_request, name='password_reset_request_quick'),
    path('password-reset/confirm/', api_views.password_reset_confirm, name='password_reset_confirm_quick'),
    path('profile/update/', api_views.update_client_profile_quick, name='update_profile_quick'),
    path('profile/check-completeness/', api_views.check_profile_completeness, name='check_profile_completeness'),
    path('terms/check-acceptance/', api_views.check_terms_acceptance, name='check_terms_acceptance'),
    path('terms/accept/', api_views.accept_terms_of_service, name='accept_terms_of_service'),
    
    # Driver Registration endpoints
    path('driver/register/', api_views.complete_driver_registration, name='complete_driver_registration'),
    path('driver/registration-status/', api_views.get_driver_registration_status, name='get_driver_registration_status'),
    
    # User Preferences & Security Settings
    path('preferences/', api_views.UserPreferencesView.as_view(), name='user_preferences'),
    path('security/', api_views.UserSecuritySettingsView.as_view(), name='user_security_settings'),
    path('security/generate-api-key/', api_views.generate_api_key, name='generate_api_key'),
    path('security/revoke-api-key/', api_views.revoke_api_key, name='revoke_api_key'),
    path('security/activity-logs/', api_views.get_user_activity_logs, name='get_user_activity_logs'),
    path('security/sessions/', api_views.get_user_sessions, name='get_user_sessions'),
    path('security/terminate-session/', api_views.terminate_user_session, name='terminate_user_session'),
    path('security/terminate-all-sessions/', api_views.terminate_all_other_sessions, name='terminate_all_other_sessions'),
    path('security/update-password/', api_views.update_password_with_security, name='update_password_with_security'),
    
    # Social Authentication
    path('auth/google/', api_views.google_social_login, name='google_social_login'),
    path('auth/apple/', api_views.apple_social_login, name='apple_social_login'),
    path('auth/social/urls/', api_views.get_social_login_urls, name='get_social_login_urls'),
    path('auth/social/disconnect/', api_views.disconnect_social_account, name='disconnect_social_account'),
    path('auth/social/accounts/', api_views.get_connected_social_accounts, name='get_connected_social_accounts'),
]

# Include router URLs
urlpatterns = api_urlpatterns + router.urls
