from time import sleep
from django.utils import timezone
from django.core.mail import send_mail
from celery import shared_task



def import_django_instance():
	"""
	Makes django environment available 
	to tasks!!
	"""
	import django
	import os
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RideNow.settings')
	django.setup()
	

@shared_task()
def create_profile(user_id):
	from accounts.models import User, UserProfile
	user = User.objects.get(id=user_id)
	UserProfile.objects.create(user=user, username=user.username, first_name=user.username, last_name="New User", email=user.email)

@shared_task()
def send_sms_alert_task(body, sms_phone):
	from .utils import send_sms_alert
	send_sms_alert(body, sms_phone)
	# print('SMS send receipt', body, sms_phone)
	

@shared_task()
def send_email_task(email, subject, message, is_html=False):
	from .utils import send_email_alert, send_html_email
	if is_html:
		send_html_email(email=email, subject=subject, message=message)
	else:
		send_email_alert(email, subject, message)

@shared_task()
def send_welcome_email_client_task(user_id, request_data=None):
	"""
	Send welcome email to client asynchronously
	"""
	from django.contrib.auth import get_user_model
	from django.http import HttpRequest
	from .utils import send_welcome_email_client
	
	User = get_user_model()
	try:
		user = User.objects.get(id=user_id)
		
		# Create a mock request object if request_data is provided
		request = None
		if request_data:
			request = HttpRequest()
			request.META = request_data.get('META', {})
			request.scheme = request_data.get('scheme', 'https')
			request.get_host = lambda: request_data.get('host', 'zyra.daraza.net')
		
		return send_welcome_email_client(user, request)
	except User.DoesNotExist:
		return False
	except Exception as e:
		from .models import ErrorLogs
		ErrorLogs.objects.create(
			error_narration=f"Failed to send welcome email to client {user_id}: {str(e)}"
		)
		return False

@shared_task()
def send_welcome_email_driver_task(driver_id, request_data=None):
	"""
	Send welcome email to driver asynchronously
	"""
	from accounts.models import DriverProfile
	from django.http import HttpRequest
	from .utils import send_welcome_email_driver
	
	try:
		driver = DriverProfile.objects.get(id=driver_id)
		
		# Create a mock request object if request_data is provided
		request = None
		if request_data:
			request = HttpRequest()
			request.META = request_data.get('META', {})
			request.scheme = request_data.get('scheme', 'https')
			request.get_host = lambda: request_data.get('host', 'zyra.daraza.net')
		
		return send_welcome_email_driver(driver, request)
	except DriverProfile.DoesNotExist:
		return False
	except Exception as e:
		from .models import ErrorLogs
		ErrorLogs.objects.create(
			error_narration=f"Failed to send welcome email to driver {driver_id}: {str(e)}"
		)
		return False

@shared_task()
def send_driver_approval_email_task(driver_id, request_data=None):
	"""
	Send driver approval confirmation email asynchronously
	"""
	from accounts.models import DriverProfile
	from django.http import HttpRequest
	from .utils import send_driver_approval_email
	
	try:
		driver = DriverProfile.objects.get(id=driver_id)
		
		# Create a mock request object if request_data is provided
		request = None
		if request_data:
			request = HttpRequest()
			request.META = request_data.get('META', {})
			request.scheme = request_data.get('scheme', 'https')
			request.get_host = lambda: request_data.get('host', 'zyra.daraza.net')
		
		return send_driver_approval_email(driver, request)
	except DriverProfile.DoesNotExist:
		return False
	except Exception as e:
		from .models import ErrorLogs
		ErrorLogs.objects.create(
			error_narration=f"Failed to send driver approval email for driver {driver_id}: {str(e)}"
		)
		return False

@shared_task()
def send_ride_confirmation_email_task(ride_id, request_data=None):
	"""
	Send ride confirmation email asynchronously
	"""
	from rides.models import Ride
	from django.http import HttpRequest
	from .utils import send_ride_confirmation_email
	
	try:
		ride = Ride.objects.get(id=ride_id)
		
		# Create a mock request object if request_data is provided
		request = None
		if request_data:
			request = HttpRequest()
			request.META = request_data.get('META', {})
			request.scheme = request_data.get('scheme', 'https')
			request.get_host = lambda: request_data.get('host', 'zyra.daraza.net')
		
		return send_ride_confirmation_email(ride, request)
	except Ride.DoesNotExist:
		return False
	except Exception as e:
		from .models import ErrorLogs
		ErrorLogs.objects.create(
			error_narration=f"Failed to send ride confirmation email for ride {ride_id}: {str(e)}"
		)
		return False

@shared_task()
def send_ride_completion_email_task(ride_id, request_data=None):
	"""
	Send ride completion email with receipt asynchronously
	"""
	from rides.models import Ride
	from django.http import HttpRequest
	from .utils import send_ride_completion_email
	
	try:
		ride = Ride.objects.get(id=ride_id)
		
		# Create a mock request object if request_data is provided
		request = None
		if request_data:
			request = HttpRequest()
			request.META = request_data.get('META', {})
			request.scheme = request_data.get('scheme', 'https')
			request.get_host = lambda: request_data.get('host', 'zyra.daraza.net')
		
		return send_ride_completion_email(ride, request)
	except Ride.DoesNotExist:
		return False
	except Exception as e:
		from .models import ErrorLogs
		ErrorLogs.objects.create(
			error_narration=f"Failed to send ride completion email for ride {ride_id}: {str(e)}"
		)
		return False

@shared_task()
def send_periodic_email_reports():
	"""
	Send periodic email reports to administrators
	"""
	from django.contrib.auth import get_user_model
	from django.core.mail import send_mail
	from django.conf import settings
	
	User = get_user_model()
	admin_users = User.objects.filter(is_staff=True, is_active=True)
	
	subject = "RideNow Daily Report"
	message = "This is your daily RideNow system report."
	
	for admin in admin_users:
		send_mail(
			subject,
			message,
			settings.DEFAULT_FROM_EMAIL,
			[admin.email],
			fail_silently=False,
		)

@shared_task()
def cleanup_expired_sessions():
	"""
	Clean up expired sessions from the database
	"""
	from django.contrib.sessions.models import Session
	from django.utils import timezone
	
	# Delete sessions that are older than 7 days
	expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
	count = expired_sessions.count()
	expired_sessions.delete()
	
	return f"Cleaned up {count} expired sessions"

