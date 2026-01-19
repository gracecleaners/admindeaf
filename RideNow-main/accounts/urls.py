from django.urls import include, path, re_path

from . import views
from django.contrib.auth import views as auth_views
from core.views import send_otp_view, verify_otp_view

urlpatterns = [
    # API endpoints
    path('api/', include('accounts.api_urls')),

	# Logins
	path('auth/', include('django.contrib.auth.urls')),
    
    # Profile Management
    path('profile/management/', views.profile_management, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/photos/update/', views.update_photos, name='update_photos'),
    path('profile/preferences/update/', views.update_preferences, name='update_preferences'),
    path('profile/security/update/', views.update_security, name='update_security'),
    path('profile/password/change/', views.change_password, name='change_password'),
    path('profile/account/delete/', views.delete_account, name='delete_account'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name='signup'),
    
    # Driver Registration Web Views
    path('register/driver/', views.driver_registration, name='driver_registration'),
    path('driver/verification/', views.driver_verification, name='driver_verification'),
    path('driver/registration-dashboard/', views.driver_registration_dashboard, name='driver_registration_dashboard'),
    path('driver/profile/update/', views.driver_profile_update, name='driver_profile_update'),
    path('driver/vehicle/register/', views.driver_vehicle_registration, name='driver_vehicle_registration'),
]