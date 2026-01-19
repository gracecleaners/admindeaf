# 🚀 Zyra - Quick Reference Card

## ⚡ Start Services

```bash
# 1. Start Celery (REQUIRED for emails/SMS)
cd /home/avalon/Desktop/DEV/RideNow
source venv/bin/activate
./dev_ops/start_celery_dev.sh

# 2. Start Django Server
python manage.py runserver 0.0.0.0:8001
```

---

## 🔍 Verify Setup

```bash
# Check social auth configuration
python manage.py verify_social_auth

# Check if Celery is running
ps aux | grep celery

# Check Redis status
systemctl status redis
```

---

## 🌐 Test URLs

```
Main Pages:
http://127.0.0.1:8001/                    → Landing page
http://127.0.0.1:8001/accounts/login/     → Login (with social)
http://127.0.0.1:8001/accounts/signup/    → Signup (with social)
http://127.0.0.1:8001/rides/book/         → Book ride

Social Auth:
http://127.0.0.1:8001/accounts/google/login/  → Google login
http://127.0.0.1:8001/accounts/apple/login/   → Apple login
http://127.0.0.1:8001/accounts/connections/   → Manage accounts

Admin:
http://127.0.0.1:8001/admin/                   → Django admin
```

---

## 🐛 Debug Commands

```bash
# Check error logs
python manage.py shell
>>> from core.models import ErrorLogs
>>> ErrorLogs.objects.order_by('-created_at')[:10]

# Check social accounts
>>> from allauth.socialaccount.models import SocialAccount
>>> SocialAccount.objects.all()

# Check client profiles
>>> from accounts.models import ClientProfile
>>> ClientProfile.objects.filter(is_verified=True)

# Test email sending
>>> from core.tasks import send_email_task
>>> send_email_task.delay('test@example.com', 'Test Subject', 'Test Message')
```

---

## 📊 What Was Fixed

### Email & SMS (11 fixes):
- ✅ All Celery tasks now use `.delay()`
- ✅ Proper async execution
- ✅ Error logging enabled

### Social Auth (Complete):
- ✅ Google & Apple OAuth
- ✅ Beautiful UI (green theme)
- ✅ Client accounts only
- ✅ Modal integration
- ✅ Account linking
- ✅ Error handling

---

## 🎯 Key Features

**Social Login:**
- One-click signup for riders
- No email verification needed
- Instant ride booking
- Provider-specific branding

**Account Types:**
- Social → Clients only
- Traditional → Clients or Drivers
- Clear separation and messaging

**Security:**
- OAuth 2.0 with PKCE
- Rate limiting
- Activity logging
- Account linking by email

---

## 📁 Important Files

**Configuration:**
- `RideNow/settings.py` - All settings
- `accounts/adapters.py` - Custom auth logic
- `.env` - OAuth credentials

**Templates:**
- `templates/account/login.html` - Main login
- `templates/socialaccount/login.html` - Social confirmation
- `templates/rides/modals/login_modal.html` - Booking modal

**Documentation:**
- `docs/SOCIAL_AUTH_INTEGRATION.md` - Full guide
- `docs/SOCIAL_AUTH_QUICK_START.md` - Quick setup
- `docs/SOCIAL_AUTH_TESTING_GUIDE.md` - Testing
- `INTEGRATION_SUMMARY.txt` - Complete summary

---

## ⚠️ Remember

1. **Start Celery** before testing emails/SMS
2. **Both pages work**: `/accounts/google/login/` and `/accounts/apple/login/`
3. **Social login** creates CLIENT accounts only
4. **Drivers** must use traditional registration

---

## 📞 Quick Help

**Problem:** Emails not sending  
**Solution:** Start Celery workers

**Problem:** Social login not working  
**Solution:** Check `python manage.py verify_social_auth`

**Problem:** Wrong provider showing  
**Solution:** Dynamic template checks `provider.id`

**Problem:** Need to test  
**Solution:** See `docs/SOCIAL_AUTH_TESTING_GUIDE.md`

---

**Status:** ✅ Production Ready  
**Updated:** October 9, 2025

