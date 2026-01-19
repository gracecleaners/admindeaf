from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

app_name = 'rides'

# REST API Router
router = DefaultRouter()
router.register(r'vehicle-types', api_views.VehicleTypeViewSet, basename='vehicletype')
router.register(r'vehicles', api_views.VehicleViewSet, basename='vehicle')
router.register(r'ride-requests', api_views.RideRequestViewSet, basename='riderequest')
router.register(r'rides', api_views.RideViewSet, basename='ride')
router.register(r'ratings', api_views.RatingViewSet, basename='rating')
router.register(r'feedback', api_views.FeedBackViewSet, basename='feedback')
router.register(r'driver-locations', api_views.DriverLocationViewSet, basename='driverlocation')
router.register(r'ride-matching', api_views.RideMatchingViewSet, basename='ridematching')

urlpatterns = [
    # ==================== WEB URLS ====================
    # Home
    path('', views.home, name='home'),
    
    # Ride Requests
    path('request/', views.request_ride, name='request'),
    path('ride-requests/', views.ride_request_list, name='ride_requests'),
    path('ride-request/<int:pk>/', views.ride_request_detail, name='ride_request_detail'),
    path('ride-request/<int:pk>/accept/', views.accept_ride_request, name='accept_ride_request'),
    path('ride-request/<int:pk>/cancel/', views.cancel_ride_request, name='cancel_ride_request'),
    path('ride-request/<int:pk>/complete/', views.complete_ride, name='complete_ride'),
    path('ride-request/<int:pk>/rate/', views.rate_ride, name='rate_ride'),
    
    # Ride Tracking & History
    path('track/<int:ride_id>/', views.track_ride, name='track'),
    path('history/', views.ride_history, name='ride_history'),
    
    # Map View
    path('map/', views.map, name='map'),
    
    # Ride Booking
    path('book/', views.book_ride, name='book_ride'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver-navigation/<int:ride_id>/', views.driver_navigation, name='driver_navigation'),
    path('driver-navigation/', views.driver_navigation, name='driver_navigation_current'),
    
    # User Rides
    path('user-rides/', views.user_rides, name='user_rides'),
    
    # ==================== REST API URLS ====================
    # Router URLs (includes all ViewSets)
    path('api/', include(router.urls)),
    
    # Custom API Endpoints
    path('api/available-drivers/', api_views.available_drivers, name='available_drivers'),
    path('api/quick-ride-request/', api_views.quick_ride_request, name='quick_ride_request'),
    path('api/driver-statistics/', api_views.driver_statistics, name='driver_statistics'),
    path('api/client-statistics/', api_views.client_statistics, name='client_statistics'),
    
    # Driver Location & Matching APIs
    path('api/find-nearby-drivers/', api_views.find_nearby_drivers, name='find_nearby_drivers'),
    path('api/start-driver-matching/', api_views.start_driver_matching, name='start_driver_matching'),
    path('api/select-driver/', api_views.select_driver, name='select_driver'),
    path('api/accept-ride-match/', api_views.accept_ride_match, name='accept_ride_match'),
    path('api/decline-ride-match/', api_views.decline_ride_match, name='decline_ride_match'),
    path('api/try-next-driver/', api_views.try_next_driver, name='try_next_driver'),
    path('api/check-matching-status/', api_views.check_matching_status, name='check_matching_status'),
    
    # Navigation APIs
    path('api/update-driver-location/', api_views.update_driver_location, name='update_driver_location'),
    path('api/arrive-at-pickup/<int:ride_id>/', api_views.arrive_at_pickup, name='arrive_at_pickup'),
    path('api/start-ride/<int:ride_id>/', api_views.start_ride, name='start_ride'),
    path('api/complete-ride/<int:ride_id>/', api_views.complete_ride, name='complete_ride'),
    path('api/cancel-ride/<int:ride_id>/', api_views.cancel_ride, name='cancel_ride'),
    
    # Client tracking APIs
    path('api/get-driver-location/<int:ride_request_id>/', api_views.get_driver_location, name='get_driver_location'),
    path('api/submit-rating/', api_views.submit_rating, name='submit_rating'),
]
