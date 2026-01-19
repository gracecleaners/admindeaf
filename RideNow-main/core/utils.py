import random
import string
# import requests
from datetime import datetime

from twilio.rest import Client
import africastalking

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from .models import Action, SystemUtility, ErrorLogs, OTP

# Initialize Twilio client
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def get_utility():
    """Get or create the system utility instance."""
    try:
        utility, created = SystemUtility.objects.get_or_create(
            id=1,
            defaults={
                'root_email': settings.DEFAULT_FROM_EMAIL,
                'send_emails_alert': True,
                'send_sms_alert': True,
                'use_twilio_sms': True,
                'use_africas_taking_sms': False,
            }
        )
        return utility
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"Error getting utility: {str(e)}")
        return None

def create_action(user, verb, target=None):
    """Create an action record"""
    try:
        action = Action.objects.create(user=user, verb=verb, target=target)
        action.save()
        return action
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"Failed to create action: {str(e)}")
        return None

def info_message(user, verb, target=None):
    """Create an information message record"""
    try:
        message = Action.objects.create(user=user, verb=verb, target=target)
        message.save()
        return message
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"Failed to create info message: {str(e)}")
        return None

def send_email_alert(email, subject, message):
    """Send email alert - this function is used by other apps"""
    utility = get_utility()
    if not utility or not utility.send_emails_alert:
        ErrorLogs.objects.create(error_narration="Email alerts are disabled or utility missing")
        return False

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"Email sending failed: {str(e)}")
        return False

def send_html_email(user=None, name=None, email=None, subject='', message='', template_name='core/templates/email_template.html'):
    """Custom function to send an HTML email."""
    utility = get_utility()
    if not utility or not utility.send_emails_alert:
        ErrorLogs.objects.create(error_narration="Email alerts are disabled or utility missing")
        return False
    
    context = {
        'user': user,
        'name': name or 'User',
        'email_message': message
    }
    try:
        message_html = render_to_string(template_name, context)
        email_msg = EmailMessage(
            subject,
            message_html,
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        email_msg.content_subtype = 'html'
        email_msg.send()
        return True
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"HTML email sending failed: {str(e)}")
        return False

def send_sms_alert(body, phone_number):
    """Send SMS alert using configured provider"""

    if not phone_number:
        return {"success": False, "error": "Phone number is required"}
    
    # Convert PhoneNumber object to string if needed
    phone_number_str = str(phone_number)
    
    if phone_number_str.startswith('+'):
        phone_number = phone_number_str
    else:
        phone_number = f"+256{phone_number_str[1:]}"
    
    utility = get_utility()
    if not utility:
        error_msg = "SystemUtility object is required but missing"
        ErrorLogs.objects.create(error_narration=error_msg)
        raise Exception(error_msg)

    if not utility.send_sms_alert:
        error_msg = "SMS alerts are disabled in system settings"
        ErrorLogs.objects.create(error_narration=error_msg)
        raise Exception(error_msg)

    if utility.use_twilio_sms:
        try:
            response = client.messages.create(
                body=body,
                to=str(phone_number),
                from_=settings.TWILIO_PHONE_NUMBER
            )
            return {"success": True, "sid": response.sid}
        except Exception as e:
            ErrorLogs.objects.create(error_narration=f"Twilio SMS error: {str(e)}")
            raise Exception(f"Failed to send SMS via Twilio: {str(e)}")
    
    elif utility.use_africas_taking_sms:
        try:
            africastalking.initialize(
                settings.AFRICAS_TALKING_USERNAME,
                settings.AFRICAS_TALKING_APIKEY
            )
            sms = africastalking.SMS
            response = sms.send(body, [str(phone_number)])
            return {"success": True, "response": response}
        except Exception as e:
            ErrorLogs.objects.create(error_narration=f"AfricasTalking SMS error: {str(e)}")
            raise Exception(f"Failed to send SMS via AfricasTalking: {str(e)}")
    
    error_msg = "No SMS service is configured"
    ErrorLogs.objects.create(error_narration=error_msg)
    raise Exception(error_msg)

def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_twilio(phone_number, otp):
    """Send OTP specifically using Twilio"""
    message = f"Your RideNow verification code is: {otp}"
    return send_sms_alert(message, phone_number)

def save_otp(phone, otp):
    """Save the generated OTP for the phone number"""
    try:
        otp_instance = OTP.objects.create(
            phone_number=phone,
            otp=otp,
            is_verified=False
        )
        return otp_instance
    except Exception as e:
        ErrorLogs.objects.create(error_narration=f"Failed to save OTP: {str(e)}")
        raise Exception(f"Failed to save OTP: {str(e)}")

def verify_otp(phone_number, otp_code):
    """Verify OTP code."""
    try:
        otp_record = OTP.objects.get(
            phone_number=phone_number,
            otp=otp_code,
            is_verified=False,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
        )
        otp_record.is_verified = True
        otp_record.save()
        return True
    except OTP.DoesNotExist:
        ErrorLogs.objects.create(
            error_narration=f"Invalid OTP verification attempt for {phone_number}"
        )
        return False
    except Exception as e:
        ErrorLogs.objects.create(
            error_narration=f"OTP verification error: {str(e)}"
        )
        return False
    
class SendOTP:
    """Class for handling OTP operations"""
    
    def send_sms(self, device, token):
        """Send OTP via SMS"""
        body = f'Your RideNow OTP Code is {token}'
        phone_number = device.number.as_e164
        return send_sms_alert(body=body, phone_number=phone_number)

    def send_email(self, device, token):
        """Send OTP via email"""
        subject = "Your RideNow OTP Code"
        context = {
            'token': token,
            'user': device.user,
            'name': device.user.get_username(),
            'email_message': 'Please use this code to log in. This code will expire in 5 minutes.'
        }
        message_html = render_to_string('core/templates/otp_email_template.html', context)
        email = EmailMessage(
            subject,
            message_html,
            settings.DEFAULT_FROM_EMAIL,
            [device.user.email],
        )
        email.content_subtype = 'html'
        try:
            email.send()
            return True
        except Exception as e:
            ErrorLogs.objects.create(error_narration=f"Failed to send OTP email: {str(e)}")
            return False

    @staticmethod
    def generate_otp(length=6):
        """Generate OTP of specified length"""
        return ''.join(random.choice(string.digits) for _ in range(length))

    @staticmethod
    def send_otp(phone_number, otp):
        """Send OTP using configured provider"""
        utility = get_utility()
        if not utility:
            raise Exception("Utility Object missing")
        
        if not utility.send_sms_alert:
            raise Exception("SMS alerts are disabled")
        
        message = f'Your RideNow verification code is: {otp}'
        
        if utility.use_twilio_sms:
            try:
                response = client.messages.create(
                    body=message,
                    to=phone_number,
                    from_=settings.TWILIO_PHONE_NUMBER
                )
                return {"success": True, "sid": response.sid}
            except Exception as e:
                ErrorLogs.objects.create(error_narration=f"Twilio SMS error: {str(e)}")
                raise Exception(f"Twilio SMS error: {str(e)}")
                
        elif utility.use_africas_taking_sms:
            try:
                africastalking.initialize(
                    settings.AFRICAS_TALKING_USERNAME,
                    settings.AFRICAS_TALKING_APIKEY
                )
                sms = africastalking.SMS
                response = sms.send(message, [phone_number])
                return {"success": True, "response": response}
            except Exception as e:
                ErrorLogs.objects.create(error_narration=f"AfricasTalking SMS error: {str(e)}")
                raise Exception(f"AfricasTalking SMS error: {str(e)}")
        
        raise Exception("No SMS service configured")

    @staticmethod
    def verify_otp(phone_number, code):
        """Verify OTP"""
        try:
            otp = OTP.objects.get(
                phone_number=phone_number,
                otp=code,
                is_verified=False,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
            )
            otp.is_verified = True
            otp.save()
            return True
        except OTP.DoesNotExist:
            return False


def normalize_phone_number(phone_number):
    """Normalize phone number"""
    if phone_number.startswith('+256'):
        return phone_number[1:]
    elif phone_number.startswith('07'):
        return f"256{phone_number[2:]}"
    elif phone_number.startswith('7'):
        return f"256{phone_number[1:]}"
    elif phone_number.startswith('256'):
        return phone_number
    else:
        return phone_number


def send_welcome_email_client(user, request=None):
    """Send beautiful welcome email to client"""
    try:
        # Prepare context for template
        context = {
            'user_name': user.get_full_name() or user.username or user.email,
            'dashboard_url': request.build_absolute_uri(reverse('rides:dashboard')) if request else 'https://zyra.daraza.net/rides/dashboard/',
            'site_name': 'Zyra',
            'support_email': 'support@zyra.daraza.net',
            'year': datetime.now().year,
        }
        
        # Render HTML template
        html_content = render_to_string('emails/welcome_client.html', context)
        
        # Create email message
        subject = f"Welcome to Zyra, {context['user_name']}! 🎉"
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = "html"  # Main content is now text/html
        
        # Send email
        email.send()
        
        # Log success
        create_action(user, f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        # Log error
        ErrorLogs.objects.create(
            error_narration=f"Failed to send welcome email to client {user.email}: {str(e)}"
        )
        return False


def send_welcome_email_driver(driver, request=None):
    """Send beautiful welcome email to driver"""
    try:
        # Prepare context for template
        context = {
            'driver_name': driver.user.get_full_name() or driver.user.username or driver.user.email,
            'driver_dashboard_url': request.build_absolute_uri(reverse('rides:driver_dashboard')) if request else 'https://zyra.daraza.net/rides/driver-dashboard/',
            'site_name': 'Zyra',
            'support_email': 'drivers@zyra.daraza.net',
            'year': datetime.now().year,
            'phone_number': str(driver.phone) if driver.phone else "Not provided",
            'vehicle_info': f"Vehicle Registration: {driver.vehicle_registration}" if driver.vehicle_registration else "Vehicle details pending",
        }
        
        # Render HTML template
        html_content = render_to_string('emails/welcome_driver.html', context)
        
        # Create email message
        subject = f"Welcome to Zyra Driver, {context['driver_name']}! 🚗"
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[driver.user.email],
        )
        email.content_subtype = "html"  # Main content is now text/html
        
        # Send email
        email.send()
        
        # Log success
        create_action(driver.user, f"Welcome email sent to driver {driver.user.email}")
        return True
        
    except Exception as e:
        # Log error
        ErrorLogs.objects.create(
            error_narration=f"Failed to send welcome email to driver {driver.user.email}: {str(e)}"
        )
        return False


def send_driver_approval_email(driver, request=None):
	"""Send driver approval confirmation email"""
	try:
		# Prepare context for template
		context = {
			'driver_name': driver.user.get_full_name() or driver.user.username or driver.user.email,
			'driver_id': driver.id,
			'phone_number': str(driver.phone) if driver.phone else "Not provided",
			'vehicle_info': f"Vehicle Registration: {driver.vehicle_registration}" if driver.vehicle_registration else "Vehicle details pending",
			'driver_dashboard_url': request.build_absolute_uri(reverse('rides:driver_dashboard')) if request else 'https://zyra.daraza.net/rides/driver-dashboard/',
			'site_name': 'Zyra',
			'support_email': 'drivers@zyra.daraza.net',
			'year': datetime.now().year,
		}
		
		# Render HTML template
		html_content = render_to_string('emails/driver_approval_confirmation.html', context)
		
		# Create email message
		subject = f"🎉 Congratulations! You're Approved as a Zyra Driver"
		
		email = EmailMessage(
			subject=subject,
			body=html_content,
			from_email=settings.DEFAULT_FROM_EMAIL,
			to=[driver.user.email],
		)
		email.content_subtype = "html"
		
		# Send email
		email.send()
		
		# Log success
		create_action(driver.user, f"Driver approval email sent to {driver.user.email}")
		return True
		
	except Exception as e:
		# Log error
		ErrorLogs.objects.create(
			error_narration=f"Failed to send driver approval email to {driver.user.email}: {str(e)}"
		)
		return False


def send_ride_confirmation_email(ride, request=None):
	"""Send ride confirmation email to customer"""
	try:
		# Prepare context for template
		context = {
			'customer_name': ride.client.user.get_full_name() or ride.client.user.username,
			'driver_name': ride.driver.user.get_full_name() or ride.driver.user.username,
			'pickup_location': ride.start_location,
			'destination': ride.end_location,
			'scheduled_time': ride.start_time,
			'ride_id': ride.id,
			'driver_phone': str(ride.driver.phone) if ride.driver.phone else "Not provided",
			'vehicle_info': f"Vehicle Registration: {ride.driver.vehicle_registration}" if ride.driver.vehicle_registration else "Vehicle details pending",
			'tracking_url': request.build_absolute_uri(reverse('rides:track_ride', kwargs={'ride_id': ride.id})) if request else f"https://zyra.daraza.net/rides/track/{ride.id}/",
			'site_name': 'Zyra',
			'support_email': 'support@zyra.daraza.net',
			'year': datetime.now().year,
		}
		
		# Render HTML template
		html_content = render_to_string('emails/ride_confirmation.html', context)
        
		# Create email message
		subject = f"🎉 Ride Confirmed - #{ride.id} - Zyra"
		
		email = EmailMessage(
			subject=subject,
			body=html_content,
			from_email=settings.DEFAULT_FROM_EMAIL,
			to=[ride.client.user.email],
		)
		email.content_subtype = "html"
		
		# Send email
		email.send()
		
		# Log success
		create_action(ride.client.user, f"Ride confirmation email sent for ride #{ride.id}")
		return True
		
	except Exception as e:
		# Log error
		ErrorLogs.objects.create(
			error_narration=f"Failed to send ride confirmation email for ride #{ride.id}: {str(e)}"
		)
		return False


def send_ride_completion_email(ride, request=None):
	"""Send ride completion email with receipt to customer"""
	try:
		# Calculate duration
		duration = ride.end_time - ride.start_time
		duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
		
		# Calculate distance (this should come from actual ride data in production)
		# For now, using a placeholder calculation
		distance_km = 5.2  # This should be calculated from actual route data
		distance_str = f"{distance_km} km"
		
		# Prepare context for template
		context = {
			'customer_name': ride.client.user.get_full_name() or ride.client.user.username,
			'driver_name': ride.driver.user.get_full_name() or ride.driver.user.username,
			'pickup_location': ride.start_location,
			'destination': ride.end_location,
			'start_time': ride.start_time.strftime('%B %d, %Y at %I:%M %p'),
			'end_time': ride.end_time.strftime('%B %d, %Y at %I:%M %p'),
			'duration': duration_str,
			'distance': distance_str,
			'ride_id': ride.id,
			'driver_phone': str(ride.driver.phone) if ride.driver.phone else "Not provided",
			'vehicle_info': f"Vehicle Registration: {ride.driver.vehicle_registration}" if ride.driver.vehicle_registration else "Vehicle details pending",
			'base_fare': "UGX 3,000",  # This should come from actual ride data
			'distance_charge': "UGX 2,600",  # This should come from actual ride data
			'time_charge': "UGX 1,200",  # This should come from actual ride data
			'discount': "UGX 500" if hasattr(ride, 'discount') and ride.discount else None,
			'total_amount': "UGX 6,300",  # This should come from actual ride data
			'receipt_pdf_url': request.build_absolute_uri(reverse('rides:download_receipt', kwargs={'ride_id': ride.id})) if request else f"https://zyra.daraza.net/rides/receipt/{ride.id}/download/",
			'receipt_view_url': request.build_absolute_uri(reverse('rides:view_receipt', kwargs={'ride_id': ride.id})) if request else f"https://zyra.daraza.net/rides/receipt/{ride.id}/",
			'rating_url': request.build_absolute_uri(reverse('rides:rate_ride', kwargs={'ride_id': ride.id})) if request else f"https://zyra.daraza.net/rides/rate/{ride.id}/",
			'site_name': 'Zyra',
			'support_email': 'support@zyra.daraza.net',
			'year': datetime.now().year,
		}
		
		# Render HTML template
		html_content = render_to_string('emails/ride_completion.html', context)
		
		# Create email message
		subject = f"🎉 Ride Completed - #{ride.id} - Receipt Attached - Zyra"
		
		email = EmailMessage(
			subject=subject,
			body=html_content,
			from_email=settings.DEFAULT_FROM_EMAIL,
			to=[ride.client.user.email],
		)
		email.content_subtype = "html"
		
		# Send email
		email.send()
		
		# Log success
		create_action(ride.client.user, f"Ride completion email sent for ride #{ride.id}")
		return True
		
	except Exception as e:
		# Log error
		ErrorLogs.objects.create(
			error_narration=f"Failed to send ride completion email for ride #{ride.id}: {str(e)}"
		)
		return False