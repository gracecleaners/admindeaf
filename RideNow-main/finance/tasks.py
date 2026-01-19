import re
from celery import shared_task

from .models import Payments, Ledger
from .utils import send_payment_request, update_payment_status

def import_django_instance():
	"""
	Makes django environment available 
	to tasks!!
	"""
	import django
	import os
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Flirt.settings')
	django.setup()


@shared_task()
def process_and_update_payment(payment_id):
    try:
        payment = Payments.objects.get(id=payment_id)
        # Execute the send_payment_request
        response = send_payment_request(payment.phone, payment.amount)
        # Update the payment record based on the response
        if response['status'] == 'success':
            payment.is_successful = True
            payment.note = response['message']
            Ledger.objects.create(
                user_from=payment.initiated_by,
                user_to=payment.cleared_by,
                is_credit=True,
                amount=payment.amount,
                is_valid=True,
                is_active=True,
                notes='Inbound User Payment'
            )
        elif response['status'] == 'error':
            message = response['message']
            if re.search("insufficient balance", message):
                payment.is_successful = False
                payment.declined = True
                payment.error = False
            else:
                payment.error = True
                payment.declined = False
                payment.is_successful = False
            payment.note = response['message'] 
        payment.save()  # Save the updates safely
        # Notify the WebSocket group
        update_payment_status(payment.id, payment.is_successful, payment.declined, payment.error)
    except Payments.DoesNotExist:
        # Log the error or handle it gracefully
        pass
    except Exception as e:
         print("Error: ", e)