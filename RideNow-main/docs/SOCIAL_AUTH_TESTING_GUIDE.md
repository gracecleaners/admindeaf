# Social Authentication Testing Guide

## 🧪 Complete Testing Checklist

### **Pre-Testing Setup**

#### **1. Ensure Services Are Running**
```bash
# Terminal 1: Django Server
cd /home/avalon/Desktop/DEV/RideNow
source venv/bin/activate
python manage.py runserver 0.0.0.0:8001

# Terminal 2: Celery Workers (for welcome emails)
cd /home/avalon/Desktop/DEV/RideNow
source venv/bin/activate
./dev_ops/start_celery_dev.sh

# Terminal 3: Check services
systemctl status redis  # Should be active
ps aux | grep celery    # Should show workers
```

#### **2. Verify Configuration**
```bash
python manage.py verify_social_auth
# Should show: ✅ All checks passed!
```

---

## ✅ Test Scenarios

### **Test 1: Google Social Login - New User**

**Steps:**
1. Visit `http://127.0.0.1:8001/accounts/login/`
2. Click "Sign in with Google"
3. **Verify:** Shows beautiful Google-branded page
4. **Check:** "Sign In with Google" heading
5. **Check:** "For riders only" message visible
6. **Check:** Green provider info box with Google logo
7. Click "Continue with Google"
8. Complete Google OAuth flow
9. **Verify:** Redirected to `/rides/book/`
10. **Verify:** User is logged in
11. **Check Django Admin:**
    - User created with `is_client=True`
    - ClientProfile created with `is_verified=True`
    - SocialAccount linked to user
    - UserPreferences created
    - UserSecuritySettings created
    - UserActivityLog entry exists

**Expected Result:**
- ✅ Seamless signup
- ✅ No email verification needed
- ✅ Immediately ready to book rides
- ✅ All profiles created

---

### **Test 2: Apple Social Login - New User**

**Steps:**
1. Visit `http://127.0.0.1:8001/accounts/login/`
2. Click "Sign in with Apple"
3. **Verify:** Shows Apple-branded page (BLACK theme, not blue)
4. **Check:** "Sign In with Apple" heading
5. **Check:** Apple logo and privacy messaging
6. Click "Continue with Apple"
7. Complete Apple OAuth flow
8. **Verify:** Redirected to `/rides/book/`

**Expected Result:**
- ✅ Apple-specific branding
- ✅ Client profile created
- ✅ Privacy-focused messaging

---

### **Test 3: Social Login - Existing Email**

**Scenario:** User has traditional account, tries social login

**Steps:**
1. Create user via traditional signup: `user@example.com`
2. Logout
3. Click "Sign in with Google"
4. Use Google account with same email: `user@example.com`
5. **Verify:** Social account links to existing user
6. **Check:** No duplicate user created
7. **Check:** SocialAccount added to existing User

**Expected Result:**
- ✅ Account linked
- ✅ No duplicates
- ✅ Login successful

---

### **Test 4: Modal Social Login**

**Steps:**
1. Visit `/rides/book/` (not logged in)
2. Try to book a ride
3. **Verify:** Login modal appears
4. **Check:** Google and Apple buttons visible in modal
5. Click "Sign in with Google" in modal
6. Complete OAuth
7. **Verify:** Redirected back to booking page
8. **Verify:** Can complete ride booking

**Expected Result:**
- ✅ Social buttons in modal
- ✅ Preserves booking flow
- ✅ Smooth UX

---

### **Test 5: Driver Registration Messaging**

**Steps:**
1. Visit login page
2. **Check:** "Want to drive? Register as a driver" link visible
3. Click driver registration link
4. **Verify:** Goes to traditional driver form
5. Go back to login
6. Click social login button
7. **Check:** "For riders only" message on confirmation page

**Expected Result:**
- ✅ Clear separation
- ✅ Drivers directed to proper flow

---

### **Test 6: Account Connections Page**

**Steps:**
1. Login with social account
2. Visit `/accounts/connections/`
3. **Verify:** Shows connected account
4. **Check:** Provider name and email displayed
5. Click "Disconnect"
6. **Verify:** Account disconnected
7. Click "Connect"
8. **Verify:** Re-connection works

**Expected Result:**
- ✅ Easy management
- ✅ Disconnect/reconnect works

---

### **Test 7: Error Handling**

**Steps:**
1. Click social login
2. Cancel OAuth flow (or use wrong credentials)
3. **Verify:** Shows `authentication_error.html`
4. **Check:** Friendly error message
5. **Check:** "Try Again" and "Back to Home" buttons
6. **Check:** Support contact information

**Expected Result:**
- ✅ Graceful error handling
- ✅ Clear recovery options

---

### **Test 8: Email Verification Integration**

**Steps:**
1. Create account via social login
2. **Check ErrorLogs:** No email verification errors
3. **Check:** User can immediately book rides
4. Traditional signup user:
5. **Verify:** Still requires email/phone verification

**Expected Result:**
- ✅ Social users skip verification
- ✅ Traditional users still verify

---

### **Test 9: Redirect Preservation**

**Steps:**
1. Try to access protected page: `/rides/user_rides/`
2. Gets redirected to login
3. Complete social login
4. **Verify:** Redirected back to `/rides/user_rides/`

**Expected Result:**
- ✅ Next URL preserved
- ✅ User goes to intended page

---

### **Test 10: Mobile Responsiveness**

**Steps:**
1. Open login on mobile device/narrow browser
2. **Check:** Social buttons are full width
3. **Check:** Text is readable
4. **Check:** Touch targets are adequate
5. Complete social login on mobile

**Expected Result:**
- ✅ Mobile-friendly
- ✅ Touch-optimized
- ✅ Responsive layout

---

## 🔍 What to Check in Django Admin

After each social login test:

### **User Model** (`/admin/accounts/user/`)
```
✅ Email matches social account
✅ is_client = True
✅ is_driver = False
✅ is_active = True
✅ Username generated from email
```

### **ClientProfile** (`/admin/accounts/clientprofile/`)
```
✅ User linked correctly
✅ is_verified = True
✅ is_active = True
✅ Email matches
✅ Name from social provider
```

### **SocialAccount** (`/admin/socialaccount/socialaccount/`)
```
✅ Provider (google or apple)
✅ UID from provider
✅ extra_data contains profile info
✅ Linked to correct user
```

### **UserActivityLog** (`/admin/accounts/useractivitylog/`)
```
✅ activity_type = 'login'
✅ description mentions social provider
✅ device_info contains provider details
✅ IP address captured
```

---

## 🐛 Common Issues & Solutions

### **Issue: Social buttons not showing**
**Debug:**
```bash
# Check template loads socialaccount
grep "load socialaccount" templates/account/login.html

# Verify providers in settings
python manage.py shell
>>> from django.conf import settings
>>> settings.INSTALLED_APPS
# Should include 'allauth.socialaccount.providers.google'
```

### **Issue: OAuth redirect fails**
**Debug:**
```
1. Check browser console for errors
2. Verify redirect URIs in Google/Apple console
3. Check allowed domains
4. Ensure correct protocol (http vs https)
```

### **Issue: User created but no ClientProfile**
**Debug:**
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(email='test@gmail.com')
>>> hasattr(user, 'client_profile')  # Should be True
>>> user.is_client  # Should be True
>>> user.client_profile.is_verified  # Should be True
```

### **Issue: Wrong page shows (Google page for Apple)**
**Debug:**
```bash
# Check template structure
ls -la templates/socialaccount/
ls -la templates/socialaccount/providers/

# Verify login.html uses dynamic provider
grep "provider.id" templates/socialaccount/login.html
```

---

## 📊 Performance Testing

### **Load Testing:**
```bash
# Install siege
sudo apt-get install siege

# Test social auth pages
siege -c 10 -t 30S http://127.0.0.1:8001/accounts/login/
siege -c 10 -t 30S http://127.0.0.1:8001/accounts/google/login/
```

### **Response Time Goals:**
- Login page: < 200ms
- Social confirmation page: < 150ms
- OAuth redirect: < 500ms
- Profile creation: < 1s

---

## 🎯 Success Criteria

### **Functional:**
- [x] Google login creates client account
- [x] Apple login creates client account  
- [x] Account linking works
- [x] Redirects are correct
- [x] Error handling works
- [x] Modals include social options
- [x] Driver messaging is clear

### **UX:**
- [x] Beautiful, branded UI
- [x] Green color theme (no purple)
- [x] Clear messaging
- [x] Smooth animations
- [x] Mobile responsive
- [x] Accessible

### **Technical:**
- [x] No linter errors
- [x] No console errors
- [x] Proper logging
- [x] Security measures in place
- [x] Database integrity maintained

---

## 📝 Manual Test Script

Copy and paste this into a test document and check off each item:

```
GOOGLE LOGIN - NEW USER
□ Login page loads correctly
□ Google button shows blue branding
□ Confirmation page shows Google logo
□ "For riders only" message visible
□ OAuth flow completes
□ User created in database
□ ClientProfile created
□ is_verified = True
□ Redirected to /rides/book/
□ Can book ride immediately

APPLE LOGIN - NEW USER
□ Login page loads correctly
□ Apple button shows black branding
□ Confirmation page shows Apple logo
□ "For riders only" message visible
□ OAuth flow completes
□ User created in database
□ ClientProfile created
□ Redirected to /rides/book/

ACCOUNT LINKING
□ Create traditional account
□ Logout
□ Login with social (same email)
□ No duplicate user created
□ SocialAccount linked
□ Login successful

MODALS
□ Login modal shows social buttons
□ Signup modal shows social buttons
□ Social login preserves next URL
□ Returns to booking after login

ERROR HANDLING
□ Cancel OAuth shows error page
□ Error page has "Try Again" button
□ Error page has support info
□ Logs error in ErrorLogs model

DRIVER MESSAGING
□ "Want to drive?" link on login
□ "Want to drive?" link on signup
□ "For riders only" on social pages
□ Driver registration link works
```

---

## 🚀 Production Deployment Checklist

Before deploying to production:

```
ENVIRONMENT
□ GOOGLE_OAUTH_CLIENT_ID set in production .env
□ GOOGLE_OAUTH_CLIENT_SECRET set in production .env
□ APPLE_OAUTH_CLIENT_ID set in production .env
□ APPLE_OAUTH_CLIENT_SECRET set in production .env
□ Production domain in OAuth redirect URIs

DATABASE
□ python manage.py migrate (production)
□ python manage.py verify_social_auth --fix (production)
□ SocialApp entries created in production DB

SERVERS
□ Redis running
□ Celery workers running
□ Celery beat running
□ Django server running

SECURITY
□ HTTPS enabled
□ Secure cookies configured
□ CSRF protection active
□ Rate limiting configured

MONITORING
□ Error logging active
□ Activity logging enabled
□ Email alerts configured
□ Sentry/error tracking setup
```

---

## 📞 Support

**Command:** `python manage.py verify_social_auth`  
**Logs:** Django Admin → ErrorLogs  
**Email:** support@zyra.app

---

**Happy Testing! 🎉**

