# RideNow - Architecture Overview

## Code Organization

### Separation of Concerns

The RideNow app follows a clean separation between web views and API endpoints:

```
views.py          ← Function-based views for web interface
api_views.py      ← ViewSets and API endpoints (DRF)
urls.py           ← Routes for both web and API
```

### File Responsibilities

#### 1. **models.py** - Data Layer
- Defines database models
- Business logic in model methods
- Database relationships

**Key Models:**
- `VehicleType`, `Vehicle` - Vehicle management
- `RideRequest`, `Ride` - Ride lifecycle
- `Rating`, `FeedBack` - User feedback
- `Route` - Geographic data

#### 2. **views.py** - Web View Layer (Function-Based)
All web interface views using function-based approach:
- `home_view()` - Landing page
- `request_ride_view()` - Request a ride
- `ride_request_list_view()` - List requests
- `ride_request_detail_view()` - View details
- `accept_ride_request()` - Driver accepts
- `cancel_ride_request()` - Cancel ride
- `complete_ride()` - Mark complete
- `rate_ride()` - Rate completed ride
- `track_ride_view()` - Real-time tracking
- `ride_history_view()` - View history
- `map_view()` - Map interface
- `dashboard_view()` - User dashboard

**Benefits:**
- Simple and straightforward
- Easy to understand control flow
- Direct request/response handling
- Template rendering

#### 3. **api_views.py** - API View Layer (DRF)
RESTful API endpoints using Django REST Framework:

**ViewSets:**
- `VehicleTypeViewSet` - CRUD for vehicle types
- `VehicleViewSet` - Vehicle management
- `RideRequestViewSet` - Ride request lifecycle
- `RideViewSet` - Completed rides
- `RatingViewSet` - Rating management
- `FeedBackViewSet` - Feedback management

**Custom API Functions:**
- `available_drivers()` - Find nearby drivers
- `driver_statistics()` - Driver analytics
- `client_statistics()` - Client analytics

**Benefits:**
- Automatic CRUD operations
- Built-in serialization
- Authentication/permission handling
- Standardized REST endpoints

#### 4. **serializers.py** - Data Serialization
Converts between Python objects and JSON:
- Request/Response formatting
- Data validation
- Nested relationships
- Custom fields

#### 5. **forms.py** - Form Layer
Django forms for web interface:
- `RideRequestForm` - Request ride
- `RatingForm` - Rate ride
- `FeedBackForm` - Provide feedback
- `RideRequestAcceptForm` - Accept ride
- `VehicleForm` - Manage vehicles

#### 6. **permissions.py** - Authorization Layer
Custom permission classes:
- Role-based access (Client/Driver)
- Object-level permissions
- Action-specific permissions

#### 7. **signals.py** - Event Handlers
Automatic actions on model changes:
- Ride creation on acceptance
- Status transitions
- Notification triggers

#### 8. **admin.py** - Admin Interface
Django admin customizations:
- Enhanced list displays
- Inline editors
- Bulk actions
- Custom filters

#### 9. **urls.py** - Routing Layer
URL patterns for both web and API:

```python
# Web URLs - Function-based views
path('request/', views.request_ride_view, name='request')
path('ride-requests/', views.ride_request_list_view, name='ride_requests')
# ... more web routes

# API URLs - ViewSets via router
router.register(r'ride-requests', api_views.RideRequestViewSet)
path('api/', include(router.urls))
```

---

## Request Flow

### Web Request Flow

```
User Request
    ↓
urls.py (route matching)
    ↓
views.py (function-based view)
    ↓
forms.py (validation)
    ↓
models.py (database operations)
    ↓
signals.py (post-save actions)
    ↓
Template rendering
    ↓
HTML Response
```

### API Request Flow

```
API Request (JSON)
    ↓
urls.py (route matching)
    ↓
api_views.py (ViewSet/APIView)
    ↓
permissions.py (authorization check)
    ↓
serializers.py (validation)
    ↓
models.py (database operations)
    ↓
signals.py (post-save actions)
    ↓
serializers.py (response formatting)
    ↓
JSON Response
```

---

## Design Patterns

### 1. Model-View-Template (MVT) - Web Interface
**Traditional Django pattern for web views**

```
Model ← → View (views.py) ← → Template
              ↕
            Form (forms.py)
```

### 2. Model-View-Serializer (MVS) - API
**REST API pattern using DRF**

```
Model ← → View (api_views.py) ← → Serializer
              ↕
         Permission (permissions.py)
```

### 3. Signal-Driven Architecture
**Event-driven approach for side effects**

```
Model Save → Signal → Handler → Action
(models.py)  (signals.py)
```

---

## Authentication & Authorization

### Web Views
- `@login_required` decorator
- Manual permission checks in views
- Django session authentication

### API Views
- JWT token authentication
- Custom permission classes
- DRF permission system

```python
# Web view
@login_required
def request_ride_view(request):
    if not request.user.is_client:
        messages.error(request, "Only clients can request rides.")
        return redirect('rides:home')
    # ... rest of logic

# API view
class RideRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDriverOrClient]
    # ... rest of logic
```

---

## Data Flow Examples

### Example 1: Client Requests Ride

**Web Interface:**
```
1. Client visits /rides/request/
2. views.request_ride_view() renders form
3. Client submits form
4. Form validated in views.py
5. RideRequest created in database
6. Signal triggers (ride_request_status_changed)
7. Redirect to ride list with success message
```

**API Interface:**
```
1. POST /rides/api/ride-requests/
2. api_views.RideRequestViewSet.create()
3. RideRequestCreateSerializer.validate()
4. RideRequest created in database
5. Signal triggers (ride_request_status_changed)
6. JSON response with created object
```

### Example 2: Driver Accepts Ride

**Web Interface:**
```
1. Driver visits /rides/ride-request/1/accept/
2. views.accept_ride_request() renders form
3. Driver selects vehicle and submits
4. Form validated
5. RideRequest updated (status=Accepted)
6. Signal creates Ride object
7. Redirect with success message
```

**API Interface:**
```
1. POST /rides/api/ride-requests/1/accept/
2. RideRequestViewSet.accept() custom action
3. Permission checks (IsDriver, CanAcceptRideRequest)
4. RideRequest updated (status=Accepted)
5. Signal creates Ride object
6. JSON response with updated object
```

---

## Database Schema

```
User (accounts app)
  ├── ClientProfile
  │     └── RideRequest → Ride → Rating/FeedBack
  └── DriverProfile
        └── Vehicle
            └── VehiclePhoto
            └── VehicleDocument

Route (geographic data)
  └── pickup_location (PointField)
  └── destination (PointField)
```

---

## Error Handling

### Web Views
```python
try:
    client_profile = request.user.client_profile
except ClientProfile.DoesNotExist:
    messages.error(request, "Client profile not found.")
    return redirect('rides:home')
```

### API Views
```python
try:
    driver_profile = request.user.diver_profile
except DriverProfile.DoesNotExist:
    return Response(
        {'error': 'Driver profile not found.'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

---

## Testing Strategy

### Unit Tests
- Model methods
- Form validation
- Serializer validation
- Permission classes

### Integration Tests
- View functions
- API endpoints
- Signal handlers

### End-to-End Tests
- Complete user workflows
- Web interface flows
- API request/response cycles

---

## Scalability Considerations

### Current Architecture Supports:
- ✅ Horizontal scaling (stateless views)
- ✅ Database read replicas (Django DB router)
- ✅ Caching layer (Redis integration ready)
- ✅ Async tasks (Celery for notifications)
- ✅ Load balancing (no session affinity needed for API)

### Future Enhancements:
- WebSocket for real-time updates
- Message queue for ride matching
- Distributed caching
- Microservices (if needed)

---

## Security Architecture

### Authentication
- **Web:** Django session-based
- **API:** JWT tokens (simplejwt)

### Authorization
- Role-based (Client/Driver/Admin)
- Object-level permissions
- Action-specific permissions

### Data Protection
- CSRF protection (web forms)
- XSS prevention (template escaping)
- SQL injection prevention (ORM)
- Rate limiting (recommended for production)

---

## Deployment Architecture

```
Load Balancer
    ↓
┌────────────────────────────────┐
│  Django Application Servers    │
│  (views.py + api_views.py)     │
└────────────────────────────────┘
    ↓                    ↓
┌──────────┐      ┌──────────────┐
│ Database │      │ Redis Cache  │
│ (PostGIS)│      └──────────────┘
└──────────┘              ↓
                    ┌──────────────┐
                    │ Celery Worker│
                    │ (signals.py) │
                    └──────────────┘
```

---

## Best Practices Implemented

1. **Separation of Concerns** - Web and API in separate files
2. **Function-Based Views** - Simple, explicit, easy to understand
3. **DRY Principle** - Reusable serializers, forms, permissions
4. **Single Responsibility** - Each function/class does one thing
5. **Explicit over Implicit** - Clear naming, obvious behavior
6. **Security First** - Authentication and authorization on all endpoints
7. **Documentation** - Comprehensive docs and docstrings
8. **Type Hints** - (Can be added for better IDE support)

---

## Development Workflow

### Adding a New Feature

1. **Define Model** (models.py)
2. **Create Migration** (`python manage.py makemigrations`)
3. **Add Serializer** (serializers.py) - for API
4. **Add Form** (forms.py) - for web
5. **Create Web View** (views.py) - function-based
6. **Create API View** (api_views.py) - if needed
7. **Add URLs** (urls.py)
8. **Create Templates** (templates/)
9. **Add Permissions** (permissions.py) - if needed
10. **Add Signals** (signals.py) - for automation
11. **Update Admin** (admin.py)
12. **Write Tests**
13. **Update Documentation**

---

## Conclusion

The RideNow architecture provides:
- ✅ Clear separation between web and API
- ✅ Function-based views for simplicity
- ✅ Scalable and maintainable structure
- ✅ Security built-in at every layer
- ✅ Ready for production deployment

**Key Principle:** Keep it simple, explicit, and secure.

