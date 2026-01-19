# RideNow API Reference

## Base URL
```
http://localhost:8000/rides/api/
```

## Authentication
All endpoints require JWT authentication unless specified otherwise.

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/token/" \
  -d "username=user&password=pass"

# Use token in requests
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/rides/api/ride-requests/"
```

---

## Endpoints

### 1. Vehicle Types

#### List Vehicle Types
```http
GET /vehicle-types/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Sedan",
    "description": "4-door passenger car",
    "engine_type": "1501cc",
    "vehicle_capacity": "4 seater"
  }
]
```

---

### 2. Vehicles

#### List Vehicles
```http
GET /vehicles/
```

**Query Parameters:**
- `type` - Filter by vehicle type ID
- `is_air_conditioned` - Filter by AC (true/false)
- `is_insured` - Filter by insurance (true/false)
- `search` - Search by name or registration

**Response:**
```json
[
  {
    "id": 1,
    "name": "Toyota Corolla",
    "registration_number": "UAH123X",
    "type_name": "Sedan",
    "is_air_conditioned": true,
    "is_insured": true
  }
]
```

#### Get Available Vehicles
```http
GET /vehicles/available/
```

Returns only vehicles with online drivers.

---

### 3. Ride Requests

#### Create Ride Request
```http
POST /ride-requests/
Content-Type: application/json
```

**Request Body:**
```json
{
  "start_location": "Kampala Road",
  "end_location": "Entebbe Airport",
  "pickup_lat": 0.3136,
  "pickup_lng": 32.5811,
  "destination_lat": 0.0424,
  "destination_lng": 32.4435,
  "vehicle": 1  // Optional
}
```

**Response:**
```json
{
  "id": 1,
  "client": 5,
  "client_details": {
    "id": 5,
    "username": "john_doe",
    "full_name": "John Doe",
    "phone": "+256700000000"
  },
  "driver": null,
  "driver_details": null,
  "vehicle": null,
  "start_location": "Kampala Road",
  "end_location": "Entebbe Airport",
  "requested_at": "2025-10-01T10:30:00Z",
  "status": "Pending",
  "created": "2025-10-01T10:30:00Z"
}
```

#### List Ride Requests
```http
GET /ride-requests/
```

**Query Parameters:**
- `status` - Filter by status (Pending, Accepted, Completed, Cancelled)
- `driver` - Filter by driver ID
- `vehicle` - Filter by vehicle ID
- `search` - Search locations

**Response:** Array of ride requests

#### Get Ride Request Details
```http
GET /ride-requests/{id}/
```

#### Accept Ride Request (Driver Only)
```http
POST /ride-requests/{id}/accept/
Content-Type: application/json
```

**Request Body:**
```json
{
  "vehicle": 2  // Optional, uses driver's default vehicle if not provided
}
```

**Response:** Updated ride request with driver assigned

#### Cancel Ride Request
```http
POST /ride-requests/{id}/cancel/
```

**Response:** Updated ride request with status "Cancelled"

#### Complete Ride (Driver Only)
```http
POST /ride-requests/{id}/complete/
```

**Response:** Updated ride request with status "Completed"

#### Get Pending Requests (Driver Only)
```http
GET /ride-requests/pending/
```

Returns all pending ride requests available for drivers to accept.

---

### 4. Rides

#### List Rides
```http
GET /rides/
```

**Query Parameters:**
- `driver` - Filter by driver ID
- `client` - Filter by client ID
- `vehicle` - Filter by vehicle ID
- `ordering` - Order by field (created, start_time, end_time)

**Response:**
```json
[
  {
    "id": 1,
    "driver": 3,
    "driver_details": {
      "id": 3,
      "username": "driver_joe",
      "full_name": "Joe Driver",
      "rating": 4.5,
      "vehicle": {
        "id": 2,
        "name": "Honda Civic"
      }
    },
    "client": 5,
    "client_details": {
      "id": 5,
      "username": "john_doe",
      "full_name": "John Doe"
    },
    "start_location": "Kampala Road",
    "end_location": "Entebbe Airport",
    "start_time": "2025-10-01T11:00:00Z",
    "end_time": "2025-10-01T12:30:00Z",
    "duration": "1:30:00",
    "created": "2025-10-01T10:30:00Z"
  }
]
```

#### Get Ride Details
```http
GET /rides/{id}/
```

---

### 5. Ratings

#### Create Rating
```http
POST /ratings/
Content-Type: application/json
```

**Request Body:**
```json
{
  "ride": 1,
  "rating": 5
}
```

**Validation:**
- Rating must be between 1 and 5
- Client can only rate their own rides
- Ride must be completed

**Response:**
```json
{
  "id": 1,
  "ride": 1,
  "ride_details": {
    "id": 1,
    "start_location": "Kampala Road",
    "end_location": "Entebbe Airport"
  },
  "client": 5,
  "client_details": {
    "id": 5,
    "username": "john_doe",
    "full_name": "John Doe"
  },
  "rating": 5,
  "created": "2025-10-01T13:00:00Z"
}
```

#### List Ratings
```http
GET /ratings/
```

**Query Parameters:**
- `ride` - Filter by ride ID
- `rating` - Filter by rating value
- `ordering` - Order by field (created, rating)

---

### 6. Feedback

#### Create Feedback
```http
POST /feedback/
Content-Type: application/json
```

**Request Body:**
```json
{
  "ride": 1,
  "message": "Great driver, very professional!",
  "rating": 1  // Optional: Link to rating
}
```

**Response:**
```json
{
  "id": 1,
  "client": 5,
  "client_details": {
    "id": 5,
    "username": "john_doe",
    "full_name": "John Doe"
  },
  "ride": 1,
  "message": "Great driver, very professional!",
  "rating": 1,
  "rating_details": {
    "id": 1,
    "rating": 5
  },
  "created": "2025-10-01T13:05:00Z"
}
```

#### List Feedback
```http
GET /feedback/
```

**Query Parameters:**
- `ride` - Filter by ride ID
- `client` - Filter by client ID

---

### 7. Statistics & Utilities

#### Get Available Drivers
```http
GET /available-drivers/
```

**Query Parameters:**
- `lat` - Latitude (optional)
- `lng` - Longitude (optional)
- `radius` - Search radius in km (default: 10)

**Response:**
```json
[
  {
    "id": 3,
    "username": "driver_joe",
    "full_name": "Joe Driver",
    "photo": "/media/users/2025/10/photo.jpg",
    "phone": "+256700000001",
    "rating": 4.5,
    "total_rides": 150,
    "vehicle_info": {
      "id": 2,
      "name": "Honda Civic",
      "type": "Sedan",
      "is_air_conditioned": true
    },
    "is_online": true
  }
]
```

#### Get Driver Statistics
```http
GET /driver-statistics/
```

**Permission:** Driver only

**Response:**
```json
{
  "total_rides": 150,
  "completed_rides": 142,
  "cancelled_rides": 8,
  "average_rating": 4.5,
  "total_ratings": 135,
  "rating_distribution": {
    "1_star": 2,
    "2_star": 5,
    "3_star": 15,
    "4_star": 50,
    "5_star": 63
  }
}
```

#### Get Client Statistics
```http
GET /client-statistics/
```

**Permission:** Client only

**Response:**
```json
{
  "total_rides": 45,
  "pending_requests": 1,
  "completed_rides": 42,
  "cancelled_rides": 2,
  "ratings_given": 40,
  "feedback_given": 38
}
```

---

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Error Response Format

```json
{
  "error": "Error message description",
  "detail": "Additional error details"
}
```

---

## Ride Request Status Flow

```
Pending → Accepted → Completed
   ↓         ↓
Cancelled  Cancelled
```

**Status Descriptions:**
- `Pending` - Waiting for driver to accept
- `Accepted` - Driver accepted, ride in progress
- `Completed` - Ride finished successfully
- `Cancelled` - Cancelled by client or driver

---

## Pagination

List endpoints support pagination:

```http
GET /ride-requests/?page=2&page_size=20
```

**Response includes:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/rides/api/ride-requests/?page=3",
  "previous": "http://localhost:8000/rides/api/ride-requests/?page=1",
  "results": [...]
}
```

---

## Filtering & Search

Use Django Filter Backend:

```http
# Multiple filters
GET /ride-requests/?status=Completed&driver=3

# Search
GET /vehicles/?search=Toyota

# Ordering
GET /rides/?ordering=-created
```

---

## Best Practices

1. **Always include Authorization header** with valid JWT token
2. **Handle errors gracefully** - Check status codes
3. **Use pagination** for large datasets
4. **Validate data client-side** before sending
5. **Cache frequently accessed data** (vehicle types, etc.)
6. **Use HTTPS** in production
7. **Implement rate limiting** on client side

---

## Example Integration (Python)

```python
import requests

class RideNowAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def request_ride(self, start_loc, end_loc, pickup_coords, dest_coords):
        """Request a new ride"""
        data = {
            'start_location': start_loc,
            'end_location': end_loc,
            'pickup_lat': pickup_coords[0],
            'pickup_lng': pickup_coords[1],
            'destination_lat': dest_coords[0],
            'destination_lng': dest_coords[1]
        }
        response = requests.post(
            f'{self.base_url}/ride-requests/',
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def get_available_drivers(self, lat, lng, radius=10):
        """Get nearby available drivers"""
        params = {'lat': lat, 'lng': lng, 'radius': radius}
        response = requests.get(
            f'{self.base_url}/available-drivers/',
            params=params,
            headers=self.headers
        )
        return response.json()
    
    def accept_ride(self, ride_request_id, vehicle_id):
        """Driver accepts a ride request"""
        response = requests.post(
            f'{self.base_url}/ride-requests/{ride_request_id}/accept/',
            json={'vehicle': vehicle_id},
            headers=self.headers
        )
        return response.json()

# Usage
api = RideNowAPI('http://localhost:8000/rides/api', 'YOUR_TOKEN')

# Request a ride
ride = api.request_ride(
    'Kampala Road',
    'Entebbe Airport',
    (0.3136, 32.5811),
    (0.0424, 32.4435)
)
print(f"Ride requested: {ride['id']}")

# Get available drivers
drivers = api.get_available_drivers(0.3136, 32.5811)
print(f"Found {len(drivers)} available drivers")
```

---

## Webhooks (Future)

Coming soon: Webhook support for real-time updates
- Ride accepted
- Ride completed
- Driver arrived
- Payment processed

---

**For more information, see the main README.md file.**

