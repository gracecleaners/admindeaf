# Quick Start Guide - RideNow Ride Ordering System

## 🚀 Getting Started in 5 Minutes

### Step 1: Ensure Dependencies
```bash
# Install required packages (if not already installed)
pip install djangorestframework django-filter djangorestframework-simplejwt
pip install django-ckeditor pillow phonenumbers django-phonenumber-field
pip install psycopg2-binary  # For PostgreSQL with PostGIS
```

### Step 2: Run Migrations
```bash
cd /home/avalon/Desktop/DEV/RideNow
python manage.py makemigrations rides
python manage.py migrate rides
```

### Step 3: Create Test Data
```bash
python manage.py shell
```

```python
from accounts.models import User, ClientProfile, DriverProfile
from rides.models import VehicleType, Vehicle

# Create a client user
client_user = User.objects.create_user(
    username='client1',
    email='client@test.com',
    password='testpass123',
    is_client=True
)

# Create client profile
client_profile = ClientProfile.objects.create(
    user=client_user,
    username='client1',
    first_name='John',
    last_name='Doe',
    email='client@test.com'
)

# Create a driver user
driver_user = User.objects.create_user(
    username='driver1',
    email='driver@test.com',
    password='testpass123',
    is_driver=True
)

# Create driver profile
driver_profile = DriverProfile.objects.create(
    user=driver_user,
    username='driver1',
    first_name='James',
    last_name='Smith',
    email='driver@test.com',
    vehicle_registration='UAH123X',
    is_verified=True,
    is_active=True,
    is_online=True
)

# Create vehicle type
vehicle_type = VehicleType.objects.create(
    name='Sedan',
    description='4-door passenger car',
    engine_type='1501cc',
    vehicle_capacity='4 seater'
)

# Create vehicle
vehicle = Vehicle.objects.create(
    type=vehicle_type,
    name='Toyota Corolla',
    registration_number='UAH123X',
    description='Clean and comfortable sedan',
    is_air_conditioned=True,
    is_insured=True,
    age='2020'
)

# Assign vehicle to driver
driver_profile.vehicle = vehicle
driver_profile.save()

print("✅ Test data created successfully!")
```

### Step 4: Access Admin Panel
```bash
# Create superuser if needed
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Visit: http://localhost:8000/admin/rides/

### Step 5: Test API Endpoints

#### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -d "username=client1&password=testpass123"
```

Save the access token from response.

#### Request a Ride
```bash
curl -X POST http://localhost:8000/rides/api/ride-requests/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Kampala Road",
    "end_location": "Entebbe Airport",
    "pickup_lat": 0.3136,
    "pickup_lng": 32.5811,
    "destination_lat": 0.0424,
    "destination_lng": 32.4435
  }'
```

#### Get Available Drivers
```bash
curl -X GET http://localhost:8000/rides/api/available-drivers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📱 Testing Complete Workflow

### 1. Client Requests Ride
```python
# As client
POST /rides/api/ride-requests/
{
  "start_location": "Kampala",
  "end_location": "Entebbe"
}
```

### 2. Driver Views Pending Requests
```python
# As driver
GET /rides/api/ride-requests/pending/
```

### 3. Driver Accepts Ride
```python
# As driver
POST /rides/api/ride-requests/1/accept/
{
  "vehicle": 1
}
```

### 4. Driver Completes Ride
```python
# As driver
POST /rides/api/ride-requests/1/complete/
```

### 5. Client Rates Ride
```python
# As client
POST /rides/api/ratings/
{
  "ride": 1,
  "rating": 5
}

POST /rides/api/feedback/
{
  "ride": 1,
  "message": "Great service!"
}
```

## 📂 File Structure

The rides app is organized into separate concerns:

```
rides/
├── views.py           ← Function-based views for web interface
├── api_views.py       ← ViewSets and API endpoints (DRF)
├── forms.py           ← Django forms for web
├── serializers.py     ← DRF serializers for API
├── permissions.py     ← Custom permissions
├── signals.py         ← Event handlers
├── models.py          ← Database models
├── admin.py           ← Admin interface
└── urls.py            ← URL routing (web + API)
```

**Benefits:**
- Clear separation between web and API
- Function-based views for simplicity
- Easy to navigate and maintain

## 🔧 Common Issues & Solutions

### Issue: "No module named 'rides.signals'"
**Solution:** Make sure `rides/signals.py` exists and `apps.py` has:
```python
def ready(self):
    import rides.signals
```

### Issue: "OperationalError: no such table: rides_riderequest"
**Solution:** Run migrations:
```bash
python manage.py migrate rides
```

### Issue: "Permission denied"
**Solution:** Check user type (is_client or is_driver flag)

### Issue: "DoesNotExist: ClientProfile matching query does not exist"
**Solution:** Create profile for the user:
```python
ClientProfile.objects.create(
    user=user,
    username=user.username,
    email=user.email,
    first_name=user.first_name,
    last_name=user.last_name
)
```

## 🎯 Key Endpoints Summary

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/rides/api/ride-requests/` | POST | Request ride | Client |
| `/rides/api/ride-requests/pending/` | GET | View pending | Driver |
| `/rides/api/ride-requests/{id}/accept/` | POST | Accept ride | Driver |
| `/rides/api/ride-requests/{id}/complete/` | POST | Complete ride | Driver |
| `/rides/api/ratings/` | POST | Rate ride | Client |
| `/rides/api/available-drivers/` | GET | Find drivers | Client |
| `/rides/api/driver-statistics/` | GET | Driver stats | Driver |
| `/rides/api/client-statistics/` | GET | Client stats | Client |

## 📊 Admin Actions

1. **View all ride requests:** Admin → Rides → Ride requests
2. **Bulk accept rides:** Select rides → Actions → Mark as Accepted
3. **View driver ratings:** Admin → Rides → Ratings
4. **Monitor feedback:** Admin → Rides → Feed backs
5. **Manage vehicles:** Admin → Rides → Vehicles

## 🔐 Setting Up Authentication

### JWT Token Configuration (already done in settings.py)
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

### Get Tokens
```bash
# Login
curl -X POST http://localhost:8000/api/token/ \
  -d "username=user&password=pass"

# Refresh token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -d "refresh=REFRESH_TOKEN"
```

## 🌐 Frontend Integration Example

### JavaScript/Fetch
```javascript
// Request a ride
async function requestRide(startLoc, endLoc) {
  const response = await fetch('http://localhost:8000/rides/api/ride-requests/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start_location: startLoc,
      end_location: endLoc
    })
  });
  return await response.json();
}

// Get available drivers
async function getDrivers() {
  const response = await fetch('http://localhost:8000/rides/api/available-drivers/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
}
```

### React Example
```jsx
import { useState, useEffect } from 'react';

function RideRequestForm() {
  const [startLocation, setStartLocation] = useState('');
  const [endLocation, setEndLocation] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const response = await fetch('/rides/api/ride-requests/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        start_location: startLocation,
        end_location: endLocation
      })
    });
    
    const data = await response.json();
    console.log('Ride requested:', data);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        value={startLocation}
        onChange={(e) => setStartLocation(e.target.value)}
        placeholder="Pickup location"
      />
      <input 
        value={endLocation}
        onChange={(e) => setEndLocation(e.target.value)}
        placeholder="Destination"
      />
      <button type="submit">Request Ride</button>
    </form>
  );
}
```

## 📝 Next Steps

1. ✅ Set up push notifications for ride updates
2. ✅ Integrate payment system (already in finance app)
3. ✅ Add real-time location tracking
4. ✅ Create mobile app (Flutter frontend exists)
5. ✅ Set up SMS notifications
6. ✅ Add ride pricing calculator
7. ✅ Implement driver rating system (done)

## 📚 Additional Resources

- **Full Documentation:** See `README.md`
- **API Reference:** See `API_REFERENCE.md`
- **Models Reference:** See `models.py`
- **Admin Interface:** http://localhost:8000/admin/rides/

## 🆘 Need Help?

1. Check the documentation files
2. Review Django and DRF official docs
3. Check linting errors: `python manage.py check`
4. View logs for debugging

---

**Happy Coding! 🚗💨**

