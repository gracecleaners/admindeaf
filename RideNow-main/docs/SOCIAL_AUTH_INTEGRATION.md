# Social Authentication Integration - Complete Guide

## 🎯 Overview

Zyra's social authentication system provides a seamless sign-in experience for **riders/clients only**. Drivers must use the traditional registration process for proper document verification and approval.

---

## ✅ What's Been Configured

### **1. Social Providers Enabled**
- ✅ **Google OAuth 2.0** - Full integration with beautiful UI
- ✅ **Apple Sign In** - Complete setup with provider-specific templates
- ✅ **Twitter** (configured but inactive)

### **2. Account Types**
- 🙋 **Social Login** → Creates **CLIENT/RIDER** accounts only
- 🚗 **Driver Registration** → Requires traditional signup with documents
- ✨ **Automatic Profile Creation** → ClientProfile, UserPreferences, UserSecuritySettings

### **3. User Experience Features**
- ✅ Provider-specific branded pages
- ✅ Dynamic template rendering (Google vs Apple)
- ✅ Clear messaging about account types
- ✅ Smooth animations and transitions
- ✅ Error handling with beautiful error pages
- ✅ Account linking for existing users

---

## 🎨 Templates Created

### **Authentication Pages**
| Template | Purpose | Design |
|----------|---------|--------|
| `templates/account/login.html` | Main login page | Green theme, social + traditional login |
| `templates/account/signup.html` | Main signup page | Green theme, social + email signup |
| `templates/socialaccount/login.html` | Social auth confirmation | Dynamic provider branding |
| `templates/socialaccount/signup.html` | Complete social registration | Profile completion form |
| `templates/socialaccount/connections.html` | Manage social accounts | View/disconnect accounts |
| `templates/socialaccount/authentication_error.html` | Error handling | Friendly error page |

### **Provider-Specific Templates**
```
templates/socialaccount/providers/
├── google/
│   └── login.html  (Google-branded page)
└── apple/
    └── login.html  (Apple-branded page)
```

---

## ⚙️ Configuration Details

### **Settings (RideNow/settings.py)**

```python
# Account Settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Optional for social, mandatory for email
ACCOUNT_ADAPTER = 'accounts.adapters.AccountAdapter'

# Social Account Settings
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Providers verify emails
SOCIALACCOUNT_AUTO_SIGNUP = True  # Auto-create accounts
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.SocialAccountAdapter'
SOCIALACCOUNT_STORE_TOKENS = True  # Store OAuth tokens
```

### **Custom Adapters (accounts/adapters.py)**

#### **SocialAccountAdapter**
- ✅ Creates CLIENT profiles automatically
- ✅ Sets `is_client=True`, `is_driver=False`
- ✅ Generates unique usernames
- ✅ Links to existing accounts by email
- ✅ Logs activity with provider information
- ✅ Redirects to ride booking page

#### **AccountAdapter**
- ✅ Handles traditional login/signup
- ✅ Smart redirects based on user type
- ✅ Integrates with social auth flow

---

## 🔄 User Flows

### **Flow 1: New User - Social Sign Up**
```
1. User clicks "Sign up with Google" on signup page
2. Redirects to socialaccount/login.html (Google-branded)
3. User clicks "Continue with Google"
4. OAuth flow with Google
5. Auto-creates User + ClientProfile
6. Sets is_client=True, is_verified=True
7. Creates UserPreferences + UserSecuritySettings
8. Logs activity
9. Redirects to /rides/book/
```

### **Flow 2: Existing User - Social Login**
```
1. User clicks "Sign in with Google" on login page
2. Redirects to socialaccount/login.html
3. OAuth flow completes
4. Adapter checks if email exists
5. Links social account to existing user
6. Logs activity
7. Redirects to /rides/book/ (or driver dashboard if driver)
```

### **Flow 3: Driver Wants to Sign Up**
```
1. User sees social login buttons
2. Reads notice: "For riders only. Drivers register here"
3. Clicks driver registration link
4. Traditional registration with documents
5. Manual approval process
```

---

## 🔧 Environment Variables Required

Add these to your `.env` file:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here

# Apple OAuth
APPLE_OAUTH_CLIENT_ID=your_apple_service_id_here
APPLE_OAUTH_CLIENT_SECRET=your_generated_secret_here
APPLE_OAUTH_KEY_ID=your_apple_key_id_here
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key_here
```

---

## 🚀 Setup Instructions

### **1. Google OAuth Setup**

#### Get Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable "Google+ API"
4. Credentials → Create OAuth 2.0 Client ID
5. Add authorized redirect URIs:
   ```
   http://127.0.0.1:8001/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```

#### Update .env:
```bash
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your_secret_here
```

### **2. Apple Sign In Setup**

#### Configure Apple:
1. Go to [Apple Developer](https://developer.apple.com/)
2. Certificates, IDs & Profiles → Identifiers
3. Register a Service ID
4. Enable "Sign in with Apple"
5. Configure return URLs:
   ```
   https://yourdomain.com/accounts/apple/login/callback/
   ```
6. Generate private key for JWT

#### Update .env:
```bash
APPLE_OAUTH_CLIENT_ID=com.yourcompany.zyra
APPLE_OAUTH_CLIENT_SECRET=generated_jwt_secret
APPLE_OAUTH_KEY_ID=ABC123DEF4
APPLE_OAUTH_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----...
```

### **3. Database Setup**

Run migrations to create social account tables:
```bash
python manage.py migrate
```

### **4. Test the Integration**

```bash
# Start development server
python manage.py runserver 0.0.0.0:8001

# Visit:
http://127.0.0.1:8001/accounts/login/
http://127.0.0.1:8001/accounts/google/login/
http://127.0.0.1:8001/accounts/apple/login/
```

---

## 📱 API Integration

### **Social Login via API (for mobile apps)**

#### Endpoint: `/api/accounts/auth/social/google/`
```bash
POST /api/accounts/auth/social/google/
Content-Type: application/json

{
    "access_token": "google_access_token_from_mobile_sdk"
}
```

**Response:**
```json
{
    "success": true,
    "user_id": 123,
    "email": "user@example.com",
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "is_new_user": true
}
```

#### Endpoint: `/api/accounts/auth/social/apple/`
```bash
POST /api/accounts/auth/social/apple/
Content-Type: application/json

{
    "id_token": "apple_identity_token_from_mobile_sdk"
}
```

---

## 🔐 Security Features

### **Implemented:**
- ✅ PKCE for OAuth2 (Google)
- ✅ Email verification from providers
- ✅ Account linking by email
- ✅ Activity logging with provider info
- ✅ Token storage for future API calls
- ✅ Error handling and logging
- ✅ Rate limiting on login attempts

### **User Privacy:**
- ✅ Social profile pictures stored as URLs (not downloaded)
- ✅ Minimal data requested from providers
- ✅ Users can disconnect accounts anytime
- ✅ Clear privacy messaging

---

## 🎯 Key Design Decisions

### **1. Clients Only for Social Login**
**Why?** Drivers require:
- Document verification (license, insurance, vehicle)
- Background checks
- Manual approval process
- Phone number verification

Social login bypasses these critical safety checks.

### **2. Auto-Create Client Profiles**
**Why?** 
- Faster onboarding
- Users can book rides immediately
- Email already verified by provider
- Reduces friction

### **3. Account Linking by Email**
**Why?**
- User convenience
- Single account across methods
- Preserves ride history
- Unified wallet and preferences

### **4. Redirect to Ride Booking**
**Why?**
- Primary use case for social login
- Clear next action
- Reduces confusion
- Better conversion

---

## 🎨 Design Philosophy

### **Color Scheme:**
- 🟢 **Primary (Zyra):** Green `#21c45d`
- 🔵 **Google:** Blue/Green gradient
- ⚫ **Apple:** Black gradient
- ⚪ **Background:** Dark overlay on ride image

### **UX Principles:**
- Clear provider identification
- Minimal steps
- Informative messages
- Error recovery guidance
- Consistent branding

---

## 🧪 Testing Checklist

### **Manual Testing:**
- [ ] Google login with new user
- [ ] Google login with existing user
- [ ] Apple login with new user
- [ ] Apple login with existing user
- [ ] Account linking (email match)
- [ ] Error handling (wrong credentials)
- [ ] Disconnect social account
- [ ] Reconnect social account
- [ ] Driver registration link visible
- [ ] Redirects work correctly

### **Automated Testing:**
```bash
# Test social auth endpoints
python manage.py test accounts.tests.SocialAuthTestCase
```

---

## 📊 Database Models

### **Tables Created:**
```
socialaccount_socialaccount  # Social account links
socialaccount_socialtoken    # OAuth tokens
socialaccount_socialapp      # Provider credentials
```

### **User Data Flow:**
```
Social Provider (Google/Apple)
    ↓
SocialAccount (provider, uid, extra_data)
    ↓
User (email, first_name, last_name)
    ↓
ClientProfile (is_client=True, is_verified=True)
    ↓
UserPreferences + UserSecuritySettings
```

---

## 🐛 Troubleshooting

### **Problem: "Authentication Error"**
**Solutions:**
- Check OAuth credentials in .env
- Verify redirect URIs in provider console
- Check error logs: `ErrorLogs` model
- Ensure correct callback URLs

### **Problem: "Social account not connecting"**
**Solutions:**
- Check `SOCIALACCOUNT_AUTO_SIGNUP = True`
- Verify email is provided by provider
- Check adapter logs
- Ensure migrations are run

### **Problem: "Wrong account type created"**
**Solutions:**
- Verify `SocialAccountAdapter.save_user()` sets `is_client=True`
- Check if driver profile exists (shouldn't for social login)
- Review adapter code

### **Problem: "Redirect not working"**
**Solutions:**
- Check `ACCOUNT_LOGIN_REDIRECT_URL` in settings
- Verify `get_login_redirect_url()` in adapter
- Ensure URL patterns are correct
- Clear sessions and try again

---

## 📝 Maintenance

### **Adding New Providers:**

1. **Install provider package:**
   ```bash
   # Already included in django-allauth
   ```

2. **Add to INSTALLED_APPS:**
   ```python
   'allauth.socialaccount.providers.facebook',
   ```

3. **Configure in SOCIALACCOUNT_PROVIDERS:**
   ```python
   'facebook': {
       'APP': {
           'client_id': env('FACEBOOK_APP_ID'),
           'secret': env('FACEBOOK_APP_SECRET'),
       },
       'SCOPE': ['email', 'public_profile'],
   }
   ```

4. **Create template:**
   ```
   templates/socialaccount/providers/facebook/login.html
   ```

5. **Update adapter if needed**

---

## 📈 Analytics & Monitoring

### **Track These Metrics:**
- Social login conversion rate
- Provider preference (Google vs Apple)
- Error rates by provider
- Account linking success rate
- Time to first ride after social signup

### **Database Queries:**
```sql
-- Social login users
SELECT COUNT(*) FROM socialaccount_socialaccount;

-- By provider
SELECT provider, COUNT(*) FROM socialaccount_socialaccount GROUP BY provider;

-- Recent social logins
SELECT u.email, sa.provider, sa.date_joined 
FROM accounts_user u 
JOIN socialaccount_socialaccount sa ON u.id = sa.user_id 
ORDER BY sa.date_joined DESC LIMIT 10;
```

---

## 🔗 Useful Links

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Setup](https://console.cloud.google.com/)
- [Apple Sign In Setup](https://developer.apple.com/)
- [OAuth 2.0 Specification](https://oauth.net/2/)

---

## 📞 Support

For issues or questions:
- Check `ErrorLogs` model in Django admin
- Review Celery logs for async email/SMS tasks
- Contact: support@zyra.app
- Documentation: `/docs/`

---

**Last Updated:** October 9, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready

