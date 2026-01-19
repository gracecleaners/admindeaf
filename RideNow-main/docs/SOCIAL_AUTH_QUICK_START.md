# Social Authentication - Quick Start Guide

## 🚀 5-Minute Setup

### **Step 1: Environment Variables**

Add to your `.env` file:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_client_id_from_google_console
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_from_google

# Apple OAuth
APPLE_OAUTH_CLIENT_ID=com.yourcompany.zyra
APPLE_OAUTH_CLIENT_SECRET=your_generated_jwt_secret
APPLE_OAUTH_KEY_ID=your_key_id
APPLE_OAUTH_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----
```

### **Step 2: Verify Setup**

```bash
# Check configuration
python manage.py verify_social_auth

# Auto-create database entries
python manage.py verify_social_auth --fix
```

### **Step 3: Test**

```bash
# Start server
python manage.py runserver 0.0.0.0:8001

# Visit:
http://127.0.0.1:8001/accounts/login/
```

---

## 📋 Key Points

### **✅ What Works:**
- Google and Apple social login for **clients/riders only**
- Auto-creates ClientProfile with verified email
- Beautiful provider-specific UI
- Account linking by email
- Smart redirects to ride booking

### **❌ What Doesn't:**
- Social login for drivers (by design - drivers need document verification)
- Password-less login (social users still get password on traditional signup)

---

## 🎯 User Paths

### **For Riders:**
```
Option 1: Social Login (Fastest)
┌─────────────────────────────────┐
│ Click "Sign in with Google"     │
│ ↓                                │
│ OAuth with Google                │
│ ↓                                │
│ Auto-create Client Profile       │
│ ↓                                │
│ Redirect to /rides/book/         │
└─────────────────────────────────┘

Option 2: Email/Phone Signup
┌─────────────────────────────────┐
│ Fill signup form                 │
│ ↓                                │
│ Verify email/phone               │
│ ↓                                │
│ Create Client Profile            │
│ ↓                                │
│ Redirect to /rides/book/         │
└─────────────────────────────────┘
```

### **For Drivers:**
```
Traditional Registration Only
┌─────────────────────────────────┐
│ Visit /accounts/register/driver/│
│ ↓                                │
│ Fill detailed form               │
│ ↓                                │
│ Upload documents                 │
│ ↓                                │
│ Admin approval                   │
│ ↓                                │
│ Access driver dashboard          │
└─────────────────────────────────┘
```

---

## 🎨 UI Components

### **Login Page Features:**
- 🔵 Google button (blue branding)
- ⚫ Apple button (black branding)
- 📧 Email/phone login form
- 🔗 Links to signup and driver registration
- 💡 Banner: "Quick Sign In for Riders"

### **Social Auth Confirmation Page:**
- Dynamic provider branding
- Clear explanation of what's happening
- Continue/Cancel buttons
- Links to alternative login methods
- Security badge

### **Signup Completion:**
- Shows social profile info
- Minimal required fields
- Pre-populated data from provider
- Clear "rider account" messaging

---

## 🔒 Security

### **Implemented:**
- ✅ CSRF protection on all forms
- ✅ Rate limiting on login attempts
- ✅ OAuth PKCE for Google
- ✅ Secure token storage
- ✅ Activity logging
- ✅ Email verification via providers

### **Account Protection:**
- Users can disconnect social accounts
- Multiple login methods supported
- Password can be set later
- Security settings per user

---

## 🐛 Common Issues & Solutions

### **Issue: Social buttons not visible**
**Solution:** Check templates load `{% load socialaccount %}`

### **Issue: OAuth redirect fails**
**Solution:** 
1. Check redirect URIs in provider console
2. Ensure they match exactly (http vs https)
3. Include port for local development

### **Issue: User created but no profile**
**Solution:**
- Check `SocialAccountAdapter.save_user()` in adapters.py
- Verify ClientProfile is created
- Check logs in ErrorLogs model

### **Issue: Wrong redirect after login**
**Solution:**
- Check `get_login_redirect_url()` in adapter
- Verify user.is_client is True
- Check settings: ACCOUNT_LOGIN_REDIRECT_URL

---

## 📞 Support Commands

```bash
# Verify setup
python manage.py verify_social_auth

# Auto-fix database entries
python manage.py verify_social_auth --fix

# Check migrations
python manage.py showmigrations socialaccount

# View social accounts
python manage.py shell
>>> from allauth.socialaccount.models import SocialAccount
>>> SocialAccount.objects.all()
```

---

## ✨ Benefits

### **For Users:**
- ⚡ One-click sign up
- 🔒 Secure OAuth flow
- 📧 No email verification needed
- 🚀 Instant ride booking

### **For Business:**
- 📈 Higher conversion rates
- 👥 Easier onboarding
- 🔗 Trusted authentication
- 📊 Better user data

---

**Status:** ✅ Fully Integrated and Production Ready  
**Last Updated:** October 9, 2025

