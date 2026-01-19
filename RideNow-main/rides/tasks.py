from datetime import timedelta

from django.db import models
from django.utils import timezone

from celery import shared_task

@shared_task()
def update_driver_scores():
	"""
	Update driver scores based on recent performance
	"""
	from .models import Ride
	from accounts.models import DriverProfile
	
	# Get drivers who have completed rides in the last 30 days
	thirty_days_ago = timezone.now() - timedelta(days=30)
	drivers = DriverProfile.objects.filter(
		rides__status='completed',
		rides__completed_at__gte=thirty_days_ago
	).distinct()
	
	updated_count = 0
	for driver in drivers:
		# Calculate new score based on recent rides
		recent_rides = driver.user.rides.filter(
			status='completed',
			completed_at__gte=thirty_days_ago
		)
		
		if recent_rides.exists():
			# Simple scoring algorithm - can be enhanced
			avg_rating = recent_rides.aggregate(
				avg_rating=models.Avg('rating__rating')
			)['avg_rating'] or 0
			
			completion_rate = recent_rides.count() / max(
				recent_rides.count() + recent_rides.filter(status='cancelled').count(), 1
			)
			
			# Update driver score (weighted average)
			new_score = (avg_rating * 0.7) + (completion_rate * 100 * 0.3)
			driver.score = min(max(new_score, 0), 100)  # Clamp between 0-100
			driver.save()
			updated_count += 1
	
	return f"Updated scores for {updated_count} drivers"


@shared_task()
def cleanup_old_rides():
	"""
	Clean up old completed rides (older than 1 year)
	"""
	from .models import Ride
	
	one_year_ago = timezone.now() - timedelta(days=365)
	old_rides = Ride.objects.filter(
		status='completed',
		completed_at__lt=one_year_ago
	)
	
	count = old_rides.count()
	old_rides.delete()
	
	return f"Cleaned up {count} old rides"


@shared_task()
def send_ride_reminders():
	"""
	Send reminders for upcoming rides
	"""
	from .models import Ride
	from core.tasks import send_sms_alert_task, send_email_task
	
	# Get rides starting in the next 30 minutes
	now = timezone.now()
	reminder_time = now + timedelta(minutes=30)
	
	upcoming_rides = Ride.objects.filter(
		status='confirmed',
		scheduled_time__lte=reminder_time,
		scheduled_time__gt=now,
		reminder_sent=False
	)
	
	sent_count = 0
	for ride in upcoming_rides:
		# Send SMS reminder to customer
		if ride.customer.phone_number:
			message = f"Reminder: Your ride is scheduled in 30 minutes. Driver: {ride.driver.user.get_full_name()}"
			send_sms_alert_task.delay(message, ride.customer.phone_number)
		
		# Send email reminder
		if ride.customer.email:
			subject = "Ride Reminder - Zyra"
			message = f"Your ride is scheduled in 30 minutes with {ride.driver.user.get_full_name()}"
			send_email_task.delay(ride.customer.email, subject, message)
		
		ride.reminder_sent = True
		ride.save()
		sent_count += 1
	
	return f"Sent reminders for {sent_count} rides"
