# Social Authentication Quick Reference

## Quick Setup

### 1. Environment Variables
```bash
# Add to .env file
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
APPLE_OAUTH_CLIENT_ID=your_apple_client_id
APPLE_OAUTH_CLIENT_SECRET=your_apple_client_secret
APPLE_OAUTH_KEY_ID=your_apple_key_id
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key
```

### 2. OAuth Redirect URIs
```
# Google
https://yourdomain.com/accounts/google/login/callback/

# Apple
https://yourdomain.com/accounts/apple/login/callback/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/google/` | Google OAuth login |
| `POST` | `/api/auth/apple/` | Apple Sign In login |
| `GET` | `/api/auth/social/urls/` | Get OAuth URLs |
| `GET` | `/api/auth/social/accounts/` | Get connected accounts |
| `POST` | `/api/auth/social/disconnect/` | Disconnect account |

## Web Implementation

### HTML Buttons
```html
<a href="/accounts/google/login/" class="btn">Google Login</a>
<a href="/accounts/apple/login/" class="btn">Apple Login</a>
```

### JavaScript API
```javascript
// Google Login
fetch('/api/auth/google/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_token: googleToken })
});

// Apple Login
fetch('/api/auth/apple/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        identity_token: appleToken,
        user: { name: { firstName: 'John', lastName: 'Doe' } }
    })
});
```

## Mobile Implementation

### React Native
```javascript
// Google
import { GoogleSignin } from '@react-native-google-signin/google-signin';
const { accessToken } = await GoogleSignin.signIn();

// Apple
import { AppleAuthentication } from 'expo-apple-authentication';
const credential = await AppleAuthentication.signInAsync();
```

### Flutter
```dart
// Google
import 'package:google_sign_in/google_sign_in.dart';
final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();

// Apple
import 'package:sign_in_with_apple/sign_in_with_apple.dart';
final credential = await SignInWithApple.getAppleIDCredential();
```

## Response Format

### Success Response
```json
{
    "success": true,
    "message": "Login successful",
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_client": true,
        "is_driver": false
    },
    "redirect_url": "/rides/dashboard/"
}
```

### Error Response
```json
{
    "success": false,
    "error": "Invalid access token"
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `redirect_uri_mismatch` | Check OAuth redirect URIs in provider console |
| `invalid_client` | Verify client ID and secret |
| `access_denied` | Check OAuth scopes and permissions |
| `Invalid access token` | Ensure token is valid and not expired |

## Security Checklist

- [ ] Use HTTPS for all OAuth redirects
- [ ] Validate tokens on server side
- [ ] Implement rate limiting
- [ ] Monitor authentication logs
- [ ] Rotate OAuth secrets regularly
- [ ] Use secure token storage

## Testing

### Test OAuth Flow
```bash
# Test Google login
curl -X POST http://localhost:8000/api/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "test_token"}'

# Test Apple login
curl -X POST http://localhost:8000/api/auth/apple/ \
  -H "Content-Type: application/json" \
  -d '{"identity_token": "test_token"}'
```

### Get OAuth URLs
```bash
curl http://localhost:8000/api/auth/social/urls/
```

## Provider Configuration

### Google OAuth Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URIs
4. Configure OAuth consent screen

### Apple Developer Portal
1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Create App ID with Sign In with Apple
3. Create Service ID for web authentication
4. Generate private key for Sign In with Apple

## Support

- **Documentation**: `/docs/SOCIAL_AUTH.md`
- **API Docs**: `/api/docs/`
- **Issues**: Report bugs and feature requests
- **Contact**: Development team

---

**Quick Reference v1.0** | **Last Updated**: January 2024
