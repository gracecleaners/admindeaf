# Welcome Email Usage Guide

This guide explains how to use the beautiful welcome email templates and functions in the Zyra application.

## Overview

The application now includes beautiful HTML email templates for:
- **Client Welcome Emails** - Sent when new users register
- **Driver Welcome Emails** - Sent when new drivers join
- **Driver Approval Emails** - Sent when driver applications are approved
- **Ride Confirmation Emails** - Sent when rides are confirmed

## Email Templates

### Client Welcome Email (`templates/emails/welcome_client.html`)
- Beautiful gradient design with green theme
- Features showcase (fast booking, safety, transparent pricing, real-time tracking)
- Call-to-action button to book first ride
- App download links
- Responsive design for mobile devices

### Driver Welcome Email (`templates/emails/welcome_driver.html`)
- Green gradient theme for drivers
- Earnings highlight section
- Driver benefits (competitive earnings, flexible schedule, insurance, etc.)
- Requirements checklist
- Support contact information
- Call-to-action to driver dashboard

### Driver Approval Email (`templates/emails/driver_approval_confirmation.html`)
- Celebratory design with animated elements
- Congratulations message with approval status
- Driver profile information display
- Step-by-step next steps guide
- Earnings preview section
- Support contact information
- Call-to-action to driver dashboard

### Ride Confirmation Email (`templates/emails/ride_confirmation.html`)
- Beautiful gradient design with green theme
- Ride confirmation message with celebration
- Ride details grid (pickup, destination, time, status)
- Driver information section with contact details
- Ride ID highlight section
- Important information and instructions
- Real-time tracking call-to-action
- Support contact information
- Responsive design for mobile devices

### Ride Completion Email (`templates/emails/ride_completion.html`)
- Beautiful gradient design with green theme
- Ride completion celebration message
- **Interactive map route visualization** with animated route path
- Comprehensive ride summary with all details
- Trip details breakdown (base fare, distance, time charges)
- Receipt download section with PDF and online viewing
- Rating section to encourage feedback
- Support contact information
- Responsive design for mobile devices

## Usage Examples

### 1. Sending Welcome Email to Client (Synchronous)

```python
from core.utils import send_welcome_email_client
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='client@example.com')

# Send welcome email
success = send_welcome_email_client(user, request)
if success:
    print("Welcome email sent successfully!")
```

### 2. Sending Welcome Email to Client (Asynchronous with Celery)

```python
from core.tasks import send_welcome_email_client_task

# Send welcome email asynchronously
task = send_welcome_email_client_task.delay(user.id)
print(f"Task queued with ID: {task.id}")
```

### 3. Sending Welcome Email to Driver (Synchronous)

```python
from core.utils import send_welcome_email_driver
from rides.models import Driver

driver = Driver.objects.get(id=1)

# Send welcome email
success = send_welcome_email_driver(driver, request)
if success:
    print("Welcome email sent successfully!")
```

### 4. Sending Welcome Email to Driver (Asynchronous with Celery)

```python
from core.tasks import send_welcome_email_driver_task

# Send welcome email asynchronously
task = send_welcome_email_driver_task.delay(driver.id)
print(f"Task queued with ID: {task.id}")
```

### 5. Sending Driver Approval Email (Synchronous)

```python
from core.utils import send_driver_approval_email
from accounts.models import DriverProfile

driver = DriverProfile.objects.get(id=1)

# Send driver approval email
success = send_driver_approval_email(driver, request)
if success:
    print("Driver approval email sent successfully!")
```

### 6. Sending Driver Approval Email (Asynchronous with Celery)

```python
from core.tasks import send_driver_approval_email_task

# Send driver approval email asynchronously
task = send_driver_approval_email_task.delay(driver.id)
print(f"Task queued with ID: {task.id}")
```

### 7. Sending Ride Confirmation Email (Synchronous)

```python
from core.utils import send_ride_confirmation_email
from rides.models import Ride

ride = Ride.objects.get(id=1)

# Send ride confirmation email
success = send_ride_confirmation_email(ride, request)
if success:
    print("Ride confirmation email sent successfully!")
```

### 8. Sending Ride Confirmation Email (Asynchronous with Celery)

```python
from core.tasks import send_ride_confirmation_email_task

# Send ride confirmation email asynchronously
task = send_ride_confirmation_email_task.delay(ride.id)
print(f"Task queued with ID: {task.id}")
```

### 9. Sending Ride Completion Email (Synchronous)

```python
from core.utils import send_ride_completion_email
from rides.models import Ride

ride = Ride.objects.get(id=1)

# Send ride completion email with receipt
success = send_ride_completion_email(ride, request)
if success:
    print("Ride completion email sent successfully!")
```

### 10. Sending Ride Completion Email (Asynchronous with Celery)

```python
from core.tasks import send_ride_completion_email_task

# Send ride completion email asynchronously
task = send_ride_completion_email_task.delay(ride.id)
print(f"Task queued with ID: {task.id}")
```

## Integration in Views

### User Registration View

```python
from django.contrib.auth import get_user_model
from core.tasks import send_welcome_email_client_task

User = get_user_model()

def register_user(request):
    # ... registration logic ...
    
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Send welcome email asynchronously
    send_welcome_email_client_task.delay(user.id)
    
    return redirect('registration_success')
```

### Driver Registration View

```python
from accounts.models import DriverProfile
from core.tasks import send_welcome_email_driver_task

def register_driver(request):
    # ... driver registration logic ...
    
    driver = DriverProfile.objects.create(
        user=user,
        phone=phone_number,
        vehicle_registration=vehicle_registration,
        # ... other fields ...
    )
    
    # Send welcome email asynchronously
    send_welcome_email_driver_task.delay(driver.id)
    
    return redirect('driver_registration_success')
```

### Driver Approval View

```python
from accounts.models import DriverProfile
from core.tasks import send_driver_approval_email_task

def approve_driver(request, driver_id):
    driver = DriverProfile.objects.get(id=driver_id)
    driver.is_verified = True
    driver.is_active = True
    driver.save()
    
    # Send approval email asynchronously
    send_driver_approval_email_task.delay(driver.id)
    
    return redirect('driver_approved')
```

### Ride Confirmation View

```python
from rides.models import Ride
from core.tasks import send_ride_confirmation_email_task

def confirm_ride(request, ride_id):
    ride = Ride.objects.get(id=ride_id)
    # Update ride status if needed
    ride.save()
    
    # Send confirmation email asynchronously
    send_ride_confirmation_email_task.delay(ride.id)
    
    return redirect('ride_confirmed')
```

### Ride Completion View

```python
from rides.models import Ride
from core.tasks import send_ride_completion_email_task

def complete_ride(request, ride_id):
    ride = Ride.objects.get(id=ride_id)
    ride.status = 'completed'
    ride.end_time = timezone.now()
    ride.save()
    
    # Send completion email with receipt asynchronously
    send_ride_completion_email_task.delay(ride.id)
    
    return redirect('ride_completed')
```

## Testing Email Templates

### Using Management Command

```bash
# List available users and drivers
python manage.py test_welcome_emails --list-users

# Test client welcome email (synchronous)
python manage.py test_welcome_emails --user-id 1

# Test client welcome email (asynchronous)
python manage.py test_welcome_emails --user-id 1 --async

# Test driver welcome email (synchronous)
python manage.py test_welcome_emails --driver-id 1

# Test driver welcome email (asynchronous)
python manage.py test_welcome_emails --driver-id 1 --async

# Test driver approval email (synchronous)
python manage.py test_welcome_emails --driver-id 1 --test-approval

# Test driver approval email (asynchronous)
python manage.py test_welcome_emails --driver-id 1 --test-approval --async

# Test ride confirmation email (synchronous)
python manage.py test_welcome_emails --ride-id 1 --test-ride-confirmation

# Test ride confirmation email (asynchronous)
python manage.py test_welcome_emails --ride-id 1 --test-ride-confirmation --async

# Test ride completion email (synchronous)
python manage.py test_welcome_emails --ride-id 1 --test-ride-completion

# Test ride completion email (asynchronous)
python manage.py test_welcome_emails --ride-id 1 --test-ride-completion --async

# Test with specific email
python manage.py test_welcome_emails --email user@example.com

# Test with first available user (default)
python manage.py test_welcome_emails
```

### Manual Testing in Django Shell

```python
# Start Django shell
python manage.py shell

# Test client welcome email
from django.contrib.auth import get_user_model
from core.utils import send_welcome_email_client

User = get_user_model()
user = User.objects.first()
send_welcome_email_client(user)

# Test driver welcome email
from accounts.models import DriverProfile
from core.utils import send_welcome_email_driver

driver = DriverProfile.objects.first()
send_welcome_email_driver(driver)

# Test driver approval email
from core.utils import send_driver_approval_email

send_driver_approval_email(driver)

# Test ride confirmation email
from rides.models import Ride
from core.utils import send_ride_confirmation_email

ride = Ride.objects.first()
send_ride_confirmation_email(ride)

# Test ride completion email
from core.utils import send_ride_completion_email

send_ride_completion_email(ride)

# Test async tasks
from core.tasks import send_welcome_email_client_task, send_welcome_email_driver_task, send_driver_approval_email_task, send_ride_confirmation_email_task, send_ride_completion_email_task

# Queue async tasks
send_welcome_email_client_task.delay(user.id)
send_welcome_email_driver_task.delay(driver.id)
send_driver_approval_email_task.delay(driver.id)
send_ride_confirmation_email_task.delay(ride.id)
send_ride_completion_email_task.delay(ride.id)
```

## Email Configuration

### Settings Required

Make sure these settings are configured in `settings.py`:

```python
# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@daraza.net'
EMAIL_HOST_PASSWORD = 'your_password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@daraza.net'

# Celery configuration (for async emails)
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
```

### Template Context Variables

#### Client Welcome Email Context
- `user_name` - User's full name or username
- `dashboard_url` - Link to user dashboard
- `site_name` - Site name (Zyra)
- `support_email` - Support email address

#### Driver Welcome Email Context
- `driver_name` - Driver's full name or username
- `driver_dashboard_url` - Link to driver dashboard
- `site_name` - Site name (Zyra)
- `support_email` - Driver support email address

#### Driver Approval Email Context
- `driver_name` - Driver's full name or username
- `driver_id` - Driver's unique ID
- `phone_number` - Driver's phone number
- `vehicle_info` - Vehicle registration information
- `driver_dashboard_url` - Link to driver dashboard
- `site_name` - Site name (Zyra)
- `support_email` - Driver support email address
- `year` - Current year for copyright

#### Ride Confirmation Email Context
- `customer_name` - Customer's full name or username
- `driver_name` - Driver's full name or username
- `pickup_location` - Pickup location
- `destination` - Destination
- `scheduled_time` - Scheduled ride time
- `ride_id` - Ride unique ID
- `driver_phone` - Driver's phone number
- `vehicle_info` - Vehicle information
- `tracking_url` - Link to track the ride
- `site_name` - Site name (Zyra)
- `support_email` - Support email address
- `year` - Current year for copyright

#### Ride Completion Email Context
- `customer_name` - Customer's full name or username
- `driver_name` - Driver's full name or username
- `pickup_location` - Pickup location
- `destination` - Destination
- `start_time` - Ride start time
- `end_time` - Ride end time
- `duration` - Ride duration
- `distance` - Ride distance
- `ride_id` - Ride unique ID
- `driver_phone` - Driver's phone number
- `vehicle_info` - Vehicle information
- `base_fare` - Base fare amount
- `distance_charge` - Distance charge
- `time_charge` - Time charge
- `discount` - Discount amount (if any)
- `total_amount` - Total ride cost
- `receipt_pdf_url` - Link to download PDF receipt
- `receipt_view_url` - Link to view receipt online
- `rating_url` - Link to rate the ride
- `site_name` - Site name (Zyra)
- `support_email` - Support email address
- `year` - Current year for copyright

#### Map Route Visualization Features
- **Animated route path** with flowing gradient line
- **Start and end points** with pulsing and bouncing animations
- **Route dots** with sequential pulsing animation
- **Distance and duration display** with icons
- **Responsive design** that adapts to mobile screens
- **CSS-only animations** for email client compatibility

## Customization

### Modifying Email Templates

1. Edit the HTML templates in `templates/emails/`
2. Update the CSS styles as needed
3. Modify the context variables in the utility functions
4. Test the changes using the management command

### Adding New Email Types

1. Create new HTML template in `templates/emails/`
2. Add utility function in `core/utils.py`
3. Add Celery task in `core/tasks.py`
4. Test using management command

## Troubleshooting

### Common Issues

1. **Emails not sending**
   - Check email configuration in settings
   - Verify SMTP credentials
   - Check email logs

2. **Templates not rendering**
   - Ensure templates are in correct directory
   - Check template syntax
   - Verify context variables

3. **Async tasks not working**
   - Check Celery worker is running
   - Verify Redis connection
   - Check task logs

### Debugging

```python
# Check email configuration
from django.conf import settings
print(settings.EMAIL_HOST)
print(settings.DEFAULT_FROM_EMAIL)

# Test email sending
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test message',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
    fail_silently=False,
)

# Check Celery status
python manage.py celery_status
```

## Best Practices

1. **Always use async tasks** for email sending to avoid blocking requests
2. **Test templates** in different email clients
3. **Monitor email delivery** and handle failures gracefully
4. **Use proper error handling** in email functions
5. **Keep templates responsive** for mobile devices
6. **Include unsubscribe links** for compliance
7. **Test with real email addresses** before production

## Security Considerations

1. **Validate email addresses** before sending
2. **Rate limit email sending** to prevent abuse
3. **Use HTTPS** for all links in emails
4. **Sanitize user input** in email content
5. **Log email activities** for audit purposes
