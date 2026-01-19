# RideNow - Comprehensive Ride Ordering System

## Overview
This is a comprehensive ride-hailing application built with Django and Django REST Framework, providing full functionality for ride requests, driver matching, real-time tracking, and payment integration.

## Features

### For Clients (Passengers)
- ✅ Request rides with pickup and destination
- ✅ View available drivers nearby
- ✅ Track rides in real-time
- ✅ View ride history
- ✅ Rate and provide feedback after rides
- ✅ Cancel pending or accepted ride requests
- ✅ View personal statistics

### For Drivers
- ✅ Accept/reject ride requests
- ✅ View pending ride requests
- ✅ Mark rides as completed
- ✅ View earnings and ride history
- ✅ Manage vehicle information
- ✅ View driver statistics and ratings
- ✅ Cancel accepted rides

### Admin Features
- ✅ Comprehensive admin dashboard
- ✅ Vehicle management (types, photos, documents)
- ✅ Ride request management
- ✅ User management (drivers & clients)
- ✅ Rating and feedback monitoring
- ✅ Bulk actions for ride requests

## Project Structure

```
rides/
├── admin.py              # Admin interface configurations
├── api_views.py          # REST API ViewSets and endpoints
├── apps.py               # App configuration
├── forms.py              # Django forms for web interface
├── models.py             # Database models
├── permissions.py        # Custom API permissions
├── serializers.py        # DRF serializers
├── signals.py            # Django signals for automation
├── urls.py               # URL routing (web + API)
├── views.py              # Function-based web views
├── README.md             # This file
├── API_REFERENCE.md      # Complete API documentation
└── QUICK_START.md        # Quick start guide
```

## Models

### Core Models
1. **VehicleType** - Vehicle categories (Sedan, SUV, Motorcycle, etc.)
2. **Vehicle** - Individual vehicle information
3. **VehiclePhoto** - Vehicle images
4. **VehicleDocument** - Vehicle documents (insurance, registration)
5. **Route** - Geographic routes with pickup and destination
6. **Ride** - Actual ride instances
7. **RideRequest** - Client ride requests
8. **Rating** - Star ratings (1-5) for completed rides
9. **FeedBack** - Detailed feedback from clients

## API Endpoints

### Base URL: `/rides/api/`

#### Vehicle Management
- `GET /vehicle-types/` - List all vehicle types
- `GET /vehicles/` - List vehicles
- `GET /vehicles/{id}/` - Vehicle details
- `GET /vehicles/available/` - Available vehicles

#### Ride Requests
- `POST /ride-requests/` - Create new ride request
- `GET /ride-requests/` - List ride requests (filtered by user)
- `GET /ride-requests/{id}/` - Ride request details
- `POST /ride-requests/{id}/accept/` - Driver accepts request
- `POST /ride-requests/{id}/cancel/` - Cancel ride request
- `POST /ride-requests/{id}/complete/` - Mark ride as completed
- `GET /ride-requests/pending/` - List pending requests (drivers)

#### Rides
- `GET /rides/` - List completed rides
- `GET /rides/{id}/` - Ride details

#### Ratings & Feedback
- `POST /ratings/` - Rate a ride
- `GET /ratings/` - List ratings
- `POST /feedback/` - Submit feedback
- `GET /feedback/` - List feedback

#### Statistics
- `GET /api/driver-statistics/` - Driver performance stats
- `GET /api/client-statistics/` - Client ride stats
- `GET /api/available-drivers/` - Find available drivers nearby

## Web URLs

### Client URLs
- `/rides/` - Home page
- `/rides/request/` - Request a new ride
- `/rides/ride-requests/` - View your ride requests
- `/rides/ride-request/{id}/` - Ride request details
- `/rides/ride-request/{id}/rate/` - Rate a completed ride
- `/rides/history/` - View ride history
- `/rides/track/{id}/` - Track active ride
- `/rides/map/` - Interactive map view

### Driver URLs
- `/rides/ride-requests/` - View pending and accepted rides
- `/rides/ride-request/{id}/accept/` - Accept a ride request
- `/rides/ride-request/{id}/complete/` - Mark ride as completed
- `/rides/ride-request/{id}/cancel/` - Cancel accepted ride

## Authentication & Permissions

### Custom Permissions
- `IsDriver` - User must be a registered driver
- `IsClient` - User must be a registered client
- `IsDriverOrClient` - User must be either driver or client
- `IsRideParticipant` - User must be part of the ride
- `CanAcceptRideRequest` - Driver can accept rides
- `CanCancelRideRequest` - Can cancel own requests
- `CanRateRide` - Client can rate completed rides
- `IsVehicleOwner` - Driver owns the vehicle

### User Types
1. **Client** - Can request and rate rides
2. **Driver** - Can accept and complete rides
3. **Admin** - Full system access

## Signals & Automation

The system uses Django signals for automatic actions:

1. **Ride Request Created** - Notify nearby drivers
2. **Ride Accepted** - Create Ride object, notify client
3. **Ride Completed** - Update end time, request rating
4. **Ride Cancelled** - Notify relevant parties
5. **Rating Created** - Update driver statistics
6. **Feedback Created** - Sentiment analysis (TODO)

## Forms

### Client Forms
- `RideRequestForm` - Request a ride
- `RatingForm` - Rate completed rides
- `FeedBackForm` - Provide feedback

### Driver Forms
- `RideRequestAcceptForm` - Accept rides with vehicle selection
- `VehicleForm` - Register/update vehicles
- `VehiclePhotoForm` - Upload vehicle photos
- `VehicleDocumentForm` - Upload documents

### Search Forms
- `RideSearchForm` - Search and filter rides

## Usage Examples

### Client: Request a Ride (API)

```python
import requests

# Authentication required
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

data = {
    'start_location': 'Kampala Road, Kampala',
    'end_location': 'Entebbe Airport',
    'pickup_lat': 0.3136,
    'pickup_lng': 32.5811,
    'destination_lat': 0.0424,
    'destination_lng': 32.4435
}

response = requests.post(
    'http://localhost:8000/rides/api/ride-requests/',
    json=data,
    headers=headers
)

print(response.json())
```

### Driver: Accept Ride Request (API)

```python
# Driver accepts ride request
ride_request_id = 1

response = requests.post(
    f'http://localhost:8000/rides/api/ride-requests/{ride_request_id}/accept/',
    json={'vehicle': 5},  # Vehicle ID
    headers=headers
)

print(response.json())
```

### Rate a Ride (API)

```python
data = {
    'ride': 1,
    'rating': 5,
    'message': 'Excellent service!'
}

response = requests.post(
    'http://localhost:8000/rides/api/ratings/',
    json=data,
    headers=headers
)
```

## Integration with Finance App

The ride system is designed to integrate with the `finance` app for:
- Ride payments
- Driver earnings
- Client billing
- Transaction history

### Payment Flow
1. Client requests ride
2. Driver accepts → price calculated
3. Client pays via AirtelMoney (integrated in finance app)
4. Ride completed
5. Payment processed through Ledger system
6. Driver receives earnings

## Admin Dashboard

Access: `/admin/rides/`

### Key Admin Features
- Visual ride request management with status badges
- Quick actions (Accept, Cancel, Complete)
- Bulk operations on ride requests
- Driver and vehicle photo previews
- Rating visualization with stars
- Comprehensive filtering and search

## Installation & Setup

1. **Ensure the app is registered in settings.py:**
```python
INSTALLED_APPS = [
    # ...
    'rides',
    'rest_framework',
    'django_filters',
    'django.contrib.gis',
]
```

2. **Include URLs in main urls.py:**
```python
urlpatterns = [
    # ...
    path('rides/', include('rides.urls')),
]
```

3. **Run migrations:**
```bash
python manage.py makemigrations rides
python manage.py migrate rides
```

4. **Create superuser (if not exists):**
```bash
python manage.py createsuperuser
```

5. **Load initial data (optional):**
```bash
python manage.py loaddata vehicle_types.json
```

## Configuration

### Required Settings

```python
# settings.py

# Google Maps API Key (for map view)
GOOGLE_MAPS_API_KEY = 'your-google-maps-api-key'

# PostGIS (for geographic features)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # ... other settings
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## Testing

### Run Tests
```bash
python manage.py test rides
```

### API Testing with cURL

```bash
# Get available drivers
curl -X GET "http://localhost:8000/rides/api/available-drivers/?lat=0.3136&lng=32.5811" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create ride request
curl -X POST "http://localhost:8000/rides/api/ride-requests/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Kampala",
    "end_location": "Entebbe",
    "pickup_lat": 0.3136,
    "pickup_lng": 32.5811,
    "destination_lat": 0.0424,
    "destination_lng": 32.4435
  }'
```

## TODO / Future Enhancements

- [ ] Real-time location tracking with WebSockets
- [ ] Push notifications (FCM integration)
- [ ] Ride pricing calculator
- [ ] Driver availability scheduling
- [ ] Multi-stop rides
- [ ] Ride sharing features
- [ ] Driver verification system
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] SMS notifications
- [ ] Email notifications
- [ ] Promotional codes/discounts
- [ ] Loyalty points system

## Security Considerations

1. **Authentication** - JWT tokens required for all API endpoints
2. **Authorization** - Custom permissions ensure users can only access their own data
3. **Data Validation** - All forms and serializers include validation
4. **CSRF Protection** - Enabled for web forms
5. **Rate Limiting** - Consider adding rate limiting for production
6. **Sensitive Data** - Vehicle documents and personal info protected

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- PostGIS Documentation: https://postgis.net/documentation/

## License

This project is part of the RideNow application.

## Contributors

- Development Team
- For issues or questions, contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** October 2025

