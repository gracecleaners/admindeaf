# RideNow API Documentation

## Overview
This is a comprehensive API for the RideNow ride sharing application. The API provides endpoints for user registration, authentication, profile management, and account operations for both clients and drivers.

## Base URL
```
http://localhost:8000/accounts/api/
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication

#### 1. Client Registration
**POST** `/auth/client/signup/`

Register a new client account.

**Request Body:**
```json
{
    "email": "client@example.com",
    "phone": "+256700000000",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "country": "UG",
    "city": "Kampala"
}
```

**Response:**
```json
{
    "message": "Client registration successful. Please verify your account.",
    "user_id": 1,
    "email": "client@example.com"
}
```

#### 2. Driver Registration
**POST** `/auth/driver/signup/`

Register a new driver account.

**Request Body:**
```json
{
    "email": "driver@example.com",
    "phone": "+256700000001",
    "password": "securepassword123",
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1985-05-15",
    "gender": "F",
    "country": "UG",
    "city": "Kampala",
    "vehicle_registration": "UAB123A",
    "drivers_license_no": "DL123456"
}
```

**Response:**
```json
{
    "message": "Driver registration successful. Please verify your account.",
    "user_id": 2,
    "email": "driver@example.com"
}
```

#### 3. User Login
**POST** `/auth/login/`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
    "username_or_email_or_phone": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "user123456",
        "email": "user@example.com",
        "is_client": true,
        "is_driver": false
    }
}
```

#### 4. Account Verification
**POST** `/auth/verify/`

Verify user account with verification code.

**Request Body:**
```json
{
    "verification_code": "123456"
}
```

**Response:**
```json
{
    "message": "Account verified successfully.",
    "user_id": 1
}
```

#### 5. Resend Verification
**POST** `/auth/resend-verification/`

Resend verification code to user's email.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "message": "Verification code has been resent to your email."
}
```

#### 6. Password Reset Request
**POST** `/auth/password-reset/request/`

Request password reset for user account.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response:**
```json
{
    "message": "Password reset link has been sent to your email address."
}
```

#### 7. Password Reset Confirm
**POST** `/auth/password-reset/confirm/`

Confirm password reset with token.

**Request Body:**
```json
{
    "token": "reset_token_here",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

**Response:**
```json
{
    "message": "Password has been successfully reset. You can now log in with your new password."
}
```

#### 8. Logout
**POST** `/auth/logout/`

Logout user and blacklist refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh_token": "refresh_token_here"
}
```

**Response:**
```json
{
    "message": "Logged out successfully."
}
```

### Profile Management

#### 9. Get User Profile
**GET** `/profile/`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "id": 1,
    "username": "user123456",
    "email": "user@example.com",
    "phone_number": "+256700000000",
    "first_name": "John",
    "last_name": "Doe",
    "is_client": true,
    "is_driver": false,
    "is_banned": false,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "client_profile": {
        "id": 1,
        "username": "user123456",
        "unique_id": "123456789",
        "first_name": "John",
        "last_name": "Doe",
        "email": "user@example.com",
        "phone": "+256700000000",
        "country": "UG",
        "gender": "M",
        "date_of_birth": "1990-01-01",
        "city": "Kampala",
        "is_verified": true,
        "is_active": true,
        "is_banned": false,
        "created": "2024-01-01T00:00:00Z",
        "updated_on": "2024-01-01T12:00:00Z"
    },
    "driver_profile": null
}
```

#### 10. Update Client Profile
**GET** `/profile/client/`
**PUT** `/profile/client/`

Get or update client profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (PUT):**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "bio": "I love traveling and meeting new people",
    "interests": "Travel, Music, Sports",
    "city": "Kampala"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "user123456",
    "unique_id": "123456789",
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "phone": "+256700000000",
    "country": "UG",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "city": "Kampala",
    "bio": "I love traveling and meeting new people",
    "interests": "Travel, Music, Sports",
    "is_verified": true,
    "is_active": true,
    "is_banned": false,
    "created": "2024-01-01T00:00:00Z",
    "updated_on": "2024-01-01T12:00:00Z"
}
```

#### 11. Update Driver Profile
**GET** `/profile/driver/`
**PUT** `/profile/driver/`

Get or update driver profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (PUT):**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    "bio": "Professional driver with 5 years experience",
    "vehicle_registration": "UAB123A",
    "drivers_license_no": "DL123456"
}
```

**Response:**
```json
{
    "id": 2,
    "username": "driver123456",
    "unique_id": "987654321",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "driver@example.com",
    "phone": "+256700000001",
    "country": "UG",
    "gender": "F",
    "date_of_birth": "1985-05-15",
    "city": "Kampala",
    "bio": "Professional driver with 5 years experience",
    "vehicle_registration": "UAB123A",
    "drivers_license_no": "DL123456",
    "is_verified": true,
    "is_active": true,
    "is_banned": false,
    "created": "2024-01-01T00:00:00Z",
    "updated_on": "2024-01-01T12:00:00Z"
}
```

### Account Management

#### 12. Change Password
**POST** `/account/change-password/`

Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

**Response:**
```json
{
    "message": "Password changed successfully."
}
```

#### 13. Delete Account
**POST** `/account/delete/`

Permanently delete user account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "password": "currentpassword123",
    "reason": "No longer using the service",
    "feedback": "The app was great but I'm moving to a different city"
}
```

**Response:**
```json
{
    "message": "Account deleted successfully."
}
```

### User Reporting

#### 14. Report User
**POST** `/report/user/`

Report a user for inappropriate behavior.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "reported_user": 2,
    "complaint": "This user was rude and unprofessional during our ride."
}
```

**Response:**
```json
{
    "message": "User reported successfully.",
    "report_id": 1
}
```

#### 15. Add Report Evidence
**POST** `/report/evidence/`

Add evidence to a user report.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (multipart/form-data):**
```
report_id: 1
file: [image or document file]
```

**Response:**
```json
{
    "message": "Evidence added successfully.",
    "evidence_id": 1
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "error": "Resource not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "An internal server error occurred. Please try again later."
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Profile management: 20 requests per minute
- Other endpoints: 100 requests per minute

## API Documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Schema: `http://localhost:8000/api/schema/`

## SDKs and Libraries
The API is compatible with standard HTTP clients. Recommended libraries:
- **Python**: `requests`, `httpx`
- **JavaScript**: `axios`, `fetch`
- **Mobile**: Native HTTP clients or libraries like `Retrofit` (Android) and `Alamofire` (iOS)

## Support
For API support and questions:
- Email: support@ridenow.com
- Phone: +256789079301
- Documentation: [API Documentation](http://localhost:8000/api/docs/)
