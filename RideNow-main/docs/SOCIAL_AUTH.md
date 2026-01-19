# Social Authentication Documentation

## Overview

Zyra supports social authentication through Google and Apple Sign In, providing seamless login experiences for both web and mobile applications. The system integrates Django Allauth with custom API endpoints for external app support.

## Table of Contents

1. [Features](#features)
2. [Setup Guide](#setup-guide)
3. [API Documentation](#api-documentation)
4. [Web Integration](#web-integration)
5. [Mobile Integration](#mobile-integration)
6. [Security](#security)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)

## Features

### Supported Providers
- **Google OAuth 2.0** - Full profile and email access
- **Apple Sign In** - Identity token validation
- **Future providers** - Extensible architecture

### Capabilities
- ✅ Web-based OAuth flows
- ✅ API-based authentication for mobile apps
- ✅ Automatic user profile creation
- ✅ JWT token generation
- ✅ Session management
- ✅ Account linking and unlinking
- ✅ Activity logging
- ✅ Security monitoring

## Setup Guide

### 1. Environment Configuration

Add the following variables to your `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Apple OAuth Configuration
APPLE_OAUTH_CLIENT_ID=your_apple_client_id_here
APPLE_OAUTH_CLIENT_SECRET=your_apple_client_secret_here
APPLE_OAUTH_KEY_ID=your_apple_key_id_here
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key_here
```

### 2. Google OAuth Setup

#### 2.1 Create Google OAuth Application

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure OAuth consent screen
6. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (development)
   - `https://yourdomain.com/accounts/google/login/callback/` (production)

#### 2.2 Configure Scopes

The application requests the following scopes:
- `profile` - Basic profile information
- `email` - Email address access

### 3. Apple Sign In Setup

#### 3.1 Create Apple Developer Account

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Create an App ID with Sign In with Apple capability
3. Create a Service ID for web authentication
4. Generate a private key for Sign In with Apple

#### 3.2 Configure Apple Sign In

1. Add your domain to the Service ID configuration
2. Configure redirect URLs:
   - `http://localhost:8000/accounts/apple/login/callback/` (development)
   - `https://yourdomain.com/accounts/apple/login/callback/` (production)

## API Documentation

### Base URL
```
https://yourdomain.com/api/auth/
```

### Authentication
All API endpoints require proper authentication headers:
```http
Authorization: Bearer <access_token>
```

### Endpoints

#### 1. Google Social Login

**Endpoint:** `POST /api/auth/google/`

**Description:** Authenticate user with Google OAuth access token

**Request Body:**
```json
{
    "access_token": "google_access_token_here"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Google login successful",
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 123,
        "username": "user@example.com",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_client": true,
        "is_driver": false,
        "profile_picture": "https://lh3.googleusercontent.com/..."
    },
    "redirect_url": "/rides/dashboard/"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Invalid Google access token"
}
```

#### 2. Apple Social Login

**Endpoint:** `POST /api/auth/apple/`

**Description:** Authenticate user with Apple Sign In identity token

**Request Body:**
```json
{
    "identity_token": "apple_identity_token_here",
    "authorization_code": "apple_authorization_code_here",
    "user": {
        "name": {
            "firstName": "John",
            "lastName": "Doe"
        }
    }
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Apple login successful",
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 123,
        "username": "user@example.com",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_client": true,
        "is_driver": false
    },
    "redirect_url": "/rides/dashboard/"
}
```

#### 3. Get Social Login URLs

**Endpoint:** `GET /api/auth/social/urls/`

**Description:** Get OAuth URLs and configuration for social providers

**Response:**
```json
{
    "success": true,
    "urls": {
        "google": {
            "auth_url": "https://yourdomain.com/accounts/google/login/",
            "callback_url": "https://yourdomain.com/accounts/google/login/callback/",
            "client_id": "your_google_client_id",
            "scope": "profile email"
        },
        "apple": {
            "auth_url": "https://yourdomain.com/accounts/apple/login/",
            "callback_url": "https://yourdomain.com/accounts/apple/login/callback/",
            "client_id": "your_apple_client_id",
            "scope": "name email"
        }
    }
}
```

#### 4. Get Connected Social Accounts

**Endpoint:** `GET /api/auth/social/accounts/`

**Description:** Get list of connected social accounts for authenticated user

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "accounts": [
        {
            "id": 1,
            "provider": "google",
            "provider_display": "Google",
            "uid": "google_user_id",
            "date_joined": "2024-01-15T10:30:00Z",
            "extra_data": {
                "email": "user@example.com",
                "given_name": "John",
                "family_name": "Doe",
                "picture": "https://lh3.googleusercontent.com/..."
            }
        }
    ]
}
```

#### 5. Disconnect Social Account

**Endpoint:** `POST /api/auth/social/disconnect/`

**Description:** Disconnect a social account from user profile

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "provider": "google"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Google account disconnected successfully"
}
```

## Web Integration

### 1. Basic Implementation

#### HTML Buttons
```html
<!-- Google Login Button -->
<button id="googleLoginBtn" class="social-login-btn">
    <svg class="google-icon">...</svg>
    Continue with Google
</button>

<!-- Apple Login Button -->
<button id="appleLoginBtn" class="social-login-btn">
    <svg class="apple-icon">...</svg>
    Continue with Apple
</button>
```

#### JavaScript Implementation
```javascript
// Google Login
document.getElementById('googleLoginBtn').addEventListener('click', function() {
    window.location.href = '/accounts/google/login/';
});

// Apple Login
document.getElementById('appleLoginBtn').addEventListener('click', function() {
    window.location.href = '/accounts/apple/login/';
});
```

### 2. Advanced Implementation with API

#### Google Login with API
```javascript
async function googleLoginWithAPI(accessToken) {
    try {
        const response = await fetch('/api/auth/google/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                access_token: accessToken
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store tokens
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // Redirect to dashboard
            window.location.href = data.redirect_url;
        } else {
            console.error('Login failed:', data.error);
        }
    } catch (error) {
        console.error('Login error:', error);
    }
}
```

#### Apple Login with API
```javascript
async function appleLoginWithAPI(identityToken, userInfo) {
    try {
        const response = await fetch('/api/auth/apple/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                identity_token: identityToken,
                user: userInfo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store tokens
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // Redirect to dashboard
            window.location.href = data.redirect_url;
        } else {
            console.error('Login failed:', data.error);
        }
    } catch (error) {
        console.error('Login error:', error);
    }
}
```

### 3. Social Account Management

#### Load Connected Accounts
```javascript
async function loadConnectedAccounts() {
    try {
        const response = await fetch('/api/auth/social/accounts/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayConnectedAccounts(data.accounts);
        }
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}
```

#### Disconnect Account
```javascript
async function disconnectAccount(provider) {
    if (!confirm(`Are you sure you want to disconnect your ${provider} account?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/auth/social/disconnect/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ provider })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            loadConnectedAccounts(); // Reload the list
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error('Error disconnecting account:', error);
    }
}
```

## Mobile Integration

### 1. React Native Implementation

#### Google Sign In
```javascript
import { GoogleSignin } from '@react-native-google-signin/google-signin';

// Configure Google Sign In
GoogleSignin.configure({
    webClientId: 'your_google_web_client_id',
    offlineAccess: true,
});

// Google Login Function
const googleLogin = async () => {
    try {
        await GoogleSignin.hasPlayServices();
        const userInfo = await GoogleSignin.signIn();
        
        // Send access token to your API
        const response = await fetch('https://yourdomain.com/api/auth/google/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                access_token: userInfo.accessToken
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store tokens securely
            await SecureStore.setItemAsync('access_token', data.access);
            await SecureStore.setItemAsync('refresh_token', data.refresh);
            
            // Navigate to main app
            navigation.navigate('Dashboard');
        }
    } catch (error) {
        console.error('Google login error:', error);
    }
};
```

#### Apple Sign In
```javascript
import { AppleAuthentication } from 'expo-apple-authentication';

// Apple Login Function
const appleLogin = async () => {
    try {
        const credential = await AppleAuthentication.signInAsync({
            requestedScopes: [
                AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                AppleAuthentication.AppleAuthenticationScope.EMAIL,
            ],
        });
        
        // Send identity token to your API
        const response = await fetch('https://yourdomain.com/api/auth/apple/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                identity_token: credential.identityToken,
                user: {
                    name: {
                        firstName: credential.fullName?.givenName || '',
                        lastName: credential.fullName?.familyName || ''
                    }
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store tokens securely
            await SecureStore.setItemAsync('access_token', data.access);
            await SecureStore.setItemAsync('refresh_token', data.refresh);
            
            // Navigate to main app
            navigation.navigate('Dashboard');
        }
    } catch (error) {
        console.error('Apple login error:', error);
    }
};
```

### 2. Flutter Implementation

#### Google Sign In
```dart
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  Future<void> signInWithGoogle() async {
    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return;

      final GoogleSignInAuthentication googleAuth = 
          await googleUser.authentication;

      // Send access token to your API
      final response = await http.post(
        Uri.parse('https://yourdomain.com/api/auth/google/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'access_token': googleAuth.accessToken,
        }),
      );

      final data = jsonDecode(response.body);
      
      if (data['success']) {
        // Store tokens securely
        await _storage.write(key: 'access_token', value: data['access']);
        await _storage.write(key: 'refresh_token', value: data['refresh']);
        
        // Navigate to main app
        Get.offAllNamed('/dashboard');
      }
    } catch (error) {
      print('Google login error: $error');
    }
  }
}
```

#### Apple Sign In
```dart
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

class AuthService {
  Future<void> signInWithApple() async {
    try {
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );

      // Send identity token to your API
      final response = await http.post(
        Uri.parse('https://yourdomain.com/api/auth/apple/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'identity_token': credential.identityToken,
          'user': {
            'name': {
              'firstName': credential.givenName ?? '',
              'lastName': credential.familyName ?? '',
            }
          }
        }),
      );

      final data = jsonDecode(response.body);
      
      if (data['success']) {
        // Store tokens securely
        await _storage.write(key: 'access_token', value: data['access']);
        await _storage.write(key: 'refresh_token', value: data['refresh']);
        
        // Navigate to main app
        Get.offAllNamed('/dashboard');
      }
    } catch (error) {
      print('Apple login error: $error');
    }
  }
}
```

## Security

### 1. Token Validation

#### Google Token Validation
- Access tokens are validated against Google's userinfo endpoint
- Tokens are checked for validity and scope
- User information is extracted securely

#### Apple Token Validation
- Identity tokens are decoded and validated
- Token signature verification (recommended for production)
- User information is extracted from token claims

### 2. Data Protection

#### User Data Handling
- Minimal data collection (email, name, profile picture)
- Secure storage of social account information
- No sensitive data exposure in API responses

#### Session Management
- JWT tokens with configurable expiration
- Refresh token rotation
- Secure cookie handling for web sessions

### 3. Security Best Practices

#### Production Recommendations
1. **Enable token signature verification** for Apple Sign In
2. **Use HTTPS** for all OAuth redirects
3. **Implement rate limiting** on authentication endpoints
4. **Monitor authentication logs** for suspicious activity
5. **Regular security audits** of OAuth configurations

#### Environment Security
```bash
# Use strong, unique secrets
GOOGLE_OAUTH_CLIENT_SECRET=your_strong_secret_here
APPLE_OAUTH_CLIENT_SECRET=your_strong_secret_here

# Rotate keys regularly
# Monitor for unauthorized access
# Use environment-specific configurations
```

## Troubleshooting

### Common Issues

#### 1. Google OAuth Errors

**Error:** `redirect_uri_mismatch`
**Solution:** Ensure redirect URIs in Google Console match your application URLs

**Error:** `invalid_client`
**Solution:** Check client ID and secret configuration

**Error:** `access_denied`
**Solution:** User denied permission or scope issues

#### 2. Apple Sign In Errors

**Error:** `invalid_request`
**Solution:** Check client ID and redirect URI configuration

**Error:** `unauthorized_client`
**Solution:** Verify Service ID configuration in Apple Developer Portal

**Error:** `invalid_grant`
**Solution:** Check authorization code and identity token validity

#### 3. API Integration Issues

**Error:** `Invalid access token`
**Solution:** Ensure token is valid and not expired

**Error:** `User creation failed`
**Solution:** Check database permissions and user model configuration

**Error:** `JWT token generation failed`
**Solution:** Verify JWT configuration and secret key

### Debug Mode

Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'social_auth.log',
        },
    },
    'loggers': {
        'accounts.adapters': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Testing

#### Unit Tests
```python
from django.test import TestCase
from accounts.api_views import google_social_login

class SocialAuthTestCase(TestCase):
    def test_google_login_success(self):
        # Test successful Google login
        pass
    
    def test_apple_login_success(self):
        # Test successful Apple login
        pass
    
    def test_invalid_token_handling(self):
        # Test invalid token handling
        pass
```

#### Integration Tests
```python
import requests

def test_google_oauth_flow():
    # Test complete OAuth flow
    response = requests.post(
        'http://localhost:8000/api/auth/google/',
        json={'access_token': 'valid_google_token'}
    )
    assert response.status_code == 200
    assert response.json()['success'] == True
```

## Examples

### Complete Web Implementation

```html
<!DOCTYPE html>
<html>
<head>
    <title>Social Login Example</title>
    <style>
        .social-btn {
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            margin: 8px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            text-decoration: none;
            color: #333;
        }
        .social-btn:hover {
            background: #f5f5f5;
        }
    </style>
</head>
<body>
    <h1>Login to Zy</h1>
    
    <div class="social-login">
        <a href="/accounts/google/login/" class="social-btn">
            <svg width="20" height="20" viewBox="0 0 24 24">
                <!-- Google icon SVG -->
            </svg>
            Continue with Google
        </a>
        
        <a href="/accounts/apple/login/" class="social-btn">
            <svg width="20" height="20" viewBox="0 0 24 24">
                <!-- Apple icon SVG -->
            </svg>
            Continue with Apple
        </a>
    </div>
    
    <script>
        // Handle OAuth callbacks
        if (window.location.search.includes('error=')) {
            const urlParams = new URLSearchParams(window.location.search);
            const error = urlParams.get('error');
            alert('Login failed: ' + error);
        }
    </script>
</body>
</html>
```

### Complete Mobile Implementation

```javascript
// React Native Social Auth Service
class SocialAuthService {
    constructor() {
        this.baseURL = 'https://yourdomain.com/api/auth';
    }
    
    async googleLogin() {
        try {
            // Get Google access token
            const { accessToken } = await GoogleSignin.signIn();
            
            // Authenticate with your API
            const response = await fetch(`${this.baseURL}/google/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ access_token: accessToken })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    tokens: {
                        access: data.access,
                        refresh: data.refresh
                    },
                    user: data.user
                };
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async appleLogin() {
        try {
            // Get Apple identity token
            const credential = await AppleAuthentication.signInAsync({
                requestedScopes: [
                    AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                    AppleAuthentication.AppleAuthenticationScope.EMAIL,
                ],
            });
            
            // Authenticate with your API
            const response = await fetch(`${this.baseURL}/apple/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    identity_token: credential.identityToken,
                    user: {
                        name: {
                            firstName: credential.fullName?.givenName || '',
                            lastName: credential.fullName?.familyName || ''
                        }
                    }
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return {
                    success: true,
                    tokens: {
                        access: data.access,
                        refresh: data.refresh
                    },
                    user: data.user
                };
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

export default new SocialAuthService();
```

## Support

For additional support and questions:

1. **Documentation**: Check this guide and API documentation
2. **Issues**: Report bugs and feature requests
3. **Community**: Join our developer community
4. **Contact**: Reach out to our development team

---

**Last Updated:** January 2024  
**Version:** 1.0.0  
**Maintainer:** Zy Development Team
