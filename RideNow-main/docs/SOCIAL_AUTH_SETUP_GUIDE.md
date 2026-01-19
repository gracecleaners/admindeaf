# Social Authentication Setup Guide

## Overview

This guide provides step-by-step instructions for setting up Google OAuth 2.0 and Apple Sign In for the Zyra platform. Follow these instructions to configure social authentication in your development and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google OAuth 2.0 Setup](#google-oauth-20-setup)
3. [Apple Sign In Setup](#apple-sign-in-setup)
4. [Environment Configuration](#environment-configuration)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- [ ] Google Cloud Console account
- [ ] Apple Developer account
- [ ] Domain name (for production)
- [ ] SSL certificate (for production)
- [ ] Access to Zyra codebase
- [ ] Environment variables configuration

## Google OAuth 2.0 Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `Zyra Social Auth`
4. Select organization (if applicable)
5. Click "Create"

### Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on "Google+ API"
4. Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type
3. Click "Create"

#### App Information
```
App name: Zyra
User support email: support@zyra.com
App logo: Upload your app logo (optional)
App domain: yourdomain.com
Developer contact information: your-email@zyra.com
```

#### Scopes
Add the following scopes:
- `../auth/userinfo.email`
- `../auth/userinfo.profile`
- `openid`

#### Test Users (Development)
Add test email addresses for development testing.

### Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Select "Web application"
4. Enter name: `Zyra Web Client`

#### Authorized JavaScript Origins
```
Development:
http://localhost:8000
http://127.0.0.1:8000

Production:
https://yourdomain.com
https://www.yourdomain.com
```

#### Authorized Redirect URIs
```
Development:
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/

Production:
https://yourdomain.com/accounts/google/login/callback/
https://www.yourdomain.com/accounts/google/login/callback/
```

5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

### Step 5: Configure Google Sign-In for Mobile

#### Android Setup
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Select "Android"
4. Enter package name: `com.Zyra.app`
5. Enter SHA-1 certificate fingerprint:
   ```bash
   # Get SHA-1 fingerprint
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
   ```
6. Click "Create"

#### iOS Setup
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Select "iOS"
4. Enter bundle ID: `com.Zyra.app`
5. Click "Create"

## Apple Sign In Setup

### Step 1: Create App ID

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Navigate to "Certificates, Identifiers & Profiles"
3. Click "Identifiers" → "+"
4. Select "App IDs" → "Continue"
5. Select "App" → "Continue"

#### App ID Configuration
```
Description: Zyra App
Bundle ID: com.Zyra.app
Capabilities: 
  ✅ Sign In with Apple
  ✅ Push Notifications (if needed)
```

6. Click "Continue" → "Register"

### Step 2: Create Service ID

1. In "Identifiers", click "+"
2. Select "Services IDs" → "Continue"
3. Select "Services IDs" → "Continue"

#### Service ID Configuration
```
Description: Zyra Web Service
Identifier: com.Zyra.web.service
```

4. Click "Continue" → "Register"
5. Click on the created Service ID
6. Check "Sign In with Apple"
7. Click "Configure"

#### Sign In with Apple Configuration
```
Primary App ID: com.Zyra.app
Domains and Subdomains: yourdomain.com
Return URLs:
  https://yourdomain.com/accounts/apple/login/callback/
  https://www.yourdomain.com/accounts/apple/login/callback/
```

8. Click "Save" → "Continue" → "Register"

### Step 3: Create Private Key

1. Go to "Keys" → "+"
2. Enter key name: `Zyra Apple Sign In Key`
3. Check "Sign In with Apple"
4. Click "Configure"
5. Select Primary App ID: `com.Zyra.app`
6. Click "Save" → "Continue" → "Register"
7. Download the `.p8` file
8. Note the **Key ID**

### Step 4: Create Client Secret

Use the following script to generate the client secret:

```python
import jwt
import time
import uuid

# Configuration
TEAM_ID = "YOUR_TEAM_ID"  # Found in Apple Developer Account
CLIENT_ID = "com.Zyra.web.service"  # Service ID
KEY_ID = "YOUR_KEY_ID"  # From step 3
PRIVATE_KEY_PATH = "path/to/AuthKey_XXXXXXXXXX.p8"  # Downloaded file

# Read private key
with open(PRIVATE_KEY_PATH, 'r') as f:
    private_key = f.read()

# Create JWT
now = int(time.time())
payload = {
    'iss': TEAM_ID,
    'iat': now,
    'exp': now + 86400 * 180,  # 6 months
    'aud': 'https://appleid.apple.com',
    'sub': CLIENT_ID,
}

headers = {
    'kid': KEY_ID,
    'alg': 'ES256'
}

client_secret = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
print(f"Client Secret: {client_secret}")
```

## Environment Configuration

### Development Environment

Create a `.env` file in your project root:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Apple OAuth Configuration
APPLE_OAUTH_CLIENT_ID=com.Zyra.web.service
APPLE_OAUTH_CLIENT_SECRET=your_generated_client_secret_here
APPLE_OAUTH_KEY_ID=your_apple_key_id_here
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key_here

# Django Settings
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@Zyra.com
```

### Production Environment

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_production_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_production_google_client_secret

# Apple OAuth Configuration
APPLE_OAUTH_CLIENT_ID=com.Zyra.web.service
APPLE_OAUTH_CLIENT_SECRET=your_production_client_secret
APPLE_OAUTH_KEY_ID=your_apple_key_id
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key

# Django Settings
DEBUG=False
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/Zyra

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@Zyra.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@Zyra.com

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
```

## Testing

### 1. Test Google OAuth Flow

#### Web Testing
1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```
2. Navigate to `http://localhost:8000/accounts/login/`
3. Click "Continue with Google"
4. Complete the OAuth flow
5. Verify user is created and logged in

#### API Testing
```bash
# Test Google login API
curl -X POST http://localhost:8000/api/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "your_google_access_token"}'
```

### 2. Test Apple Sign In Flow

#### Web Testing
1. Navigate to `http://localhost:8000/accounts/login/`
2. Click "Continue with Apple"
3. Complete the Apple Sign In flow
4. Verify user is created and logged in

#### API Testing
```bash
# Test Apple login API
curl -X POST http://localhost:8000/api/auth/apple/ \
  -H "Content-Type: application/json" \
  -d '{
    "identity_token": "your_apple_identity_token",
    "user": {
      "name": {
        "firstName": "John",
        "lastName": "Doe"
      }
    }
  }'
```

### 3. Test Social Account Management

```bash
# Get connected accounts
curl -X GET http://localhost:8000/api/auth/social/accounts/ \
  -H "Authorization: Bearer your_access_token"

# Disconnect account
curl -X POST http://localhost:8000/api/auth/social/disconnect/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"provider": "google"}'
```

## Production Deployment

### 1. Update OAuth Configurations

#### Google OAuth
1. Go to Google Cloud Console
2. Update OAuth consent screen to "Production"
3. Add production domains to authorized origins
4. Update redirect URIs for production

#### Apple Sign In
1. Go to Apple Developer Portal
2. Update Service ID configuration
3. Add production domains
4. Update return URLs

### 2. Environment Variables

Update your production environment variables:

```bash
# Production OAuth credentials
GOOGLE_OAUTH_CLIENT_ID=your_production_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_production_google_client_secret
APPLE_OAUTH_CLIENT_ID=com.Zyra.web.service
APPLE_OAUTH_CLIENT_SECRET=your_production_client_secret

# Production settings
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
```

### 3. SSL Certificate

Ensure your production domain has a valid SSL certificate:

```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4. Database Migration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/static/files/;
    }

    location /media/ {
        alias /path/to/media/files/;
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Google OAuth Issues

**Error:** `redirect_uri_mismatch`
```
Solution: Check that redirect URIs in Google Console match your application URLs exactly
```

**Error:** `invalid_client`
```
Solution: Verify client ID and secret are correct
```

**Error:** `access_denied`
```
Solution: Check OAuth scopes and user permissions
```

#### 2. Apple Sign In Issues

**Error:** `invalid_request`
```
Solution: Check client ID and redirect URI configuration
```

**Error:** `unauthorized_client`
```
Solution: Verify Service ID configuration in Apple Developer Portal
```

**Error:** `invalid_grant`
```
Solution: Check authorization code and identity token validity
```

#### 3. Django Configuration Issues

**Error:** `ModuleNotFoundError: No module named 'allauth'`
```bash
Solution: Install django-allauth
pip install django-allauth
```

**Error:** `SocialApp matching query does not exist`
```bash
Solution: Create social applications in Django admin
python manage.py shell
>>> from allauth.socialaccount.models import SocialApp
>>> SocialApp.objects.create(provider='google', name='Google', client_id='your_client_id', secret='your_secret')
```

#### 4. Environment Variable Issues

**Error:** `KeyError: 'GOOGLE_OAUTH_CLIENT_ID'`
```bash
Solution: Check .env file exists and variables are loaded
python manage.py shell
>>> import os
>>> print(os.getenv('GOOGLE_OAUTH_CLIENT_ID'))
```

### Debug Mode

Enable debug logging for social authentication:

```python
# settings.py
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
        'allauth': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'accounts.adapters': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Testing Checklist

- [ ] Google OAuth flow works in development
- [ ] Apple Sign In flow works in development
- [ ] User accounts are created correctly
- [ ] JWT tokens are generated
- [ ] Social account linking works
- [ ] Social account unlinking works
- [ ] Production OAuth configurations are correct
- [ ] SSL certificates are valid
- [ ] Environment variables are set
- [ ] Database migrations are applied
- [ ] Static files are collected
- [ ] Web server is configured correctly

## Support

For additional help:

1. **Documentation**: Check other documentation files
2. **Issues**: Report bugs and feature requests
3. **Community**: Join our developer community
4. **Contact**: Reach out to our development team

---

**Setup Guide v1.0** | **Last Updated**: January 2024  
**Maintainer**: Zyra Development Team

