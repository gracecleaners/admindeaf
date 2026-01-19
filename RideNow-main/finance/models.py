import uuid
import logging
import requests

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from core.utils import send_email_alert
from core.tasks import send_email_task, send_sms_alert_task
from accounts.models import User, DriverProfile 

from django.utils import timezone
from django.contrib.gis.db import models

from ckeditor.fields import RichTextField

from rides.models import Route, VehicleType 
from accounts.models import User, ClientProfile, DriverProfile


logger = logging.getLogger(__name__)

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name=_('billing_address_user'))
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    street = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Billing Address'
        verbose_name_plural = "Billing Addresses"


class Ledger(models.Model):
    user_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name=_('user_to'), editable=False)
    user_from = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name=_('user_from'), editable=False)
    transaction_id = models.UUIDField(unique=True, null=False, blank=False, default=uuid.uuid4(), verbose_name=_("Transaction Id"), editable=False)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, null=True, blank=True, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=9, editable=False)
    is_credit = models.BooleanField(default=False, editable=False)
    is_debit = models.BooleanField(default=False, editable=False)
    is_valid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # Set ledger for another transaction
    is_merged = models.BooleanField(default=False, editable=False)
    notes = models.CharField(max_length=150, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.transaction_id = uuid.uuid4()
        if self.is_merged == True:
            self.is_active = False
        super(Ledger, self).save(*args, **kwargs)

    # def delete(self):
    #     self.is_valid = False
    #     self.save()

    def __str__(self):
        return str(f'Transaction of {self.amount} with ID {self.transaction_id} on {self.timestamp}')


class PaymentMethods(models.Model):
    name = models.CharField(max_length=75)
    image = models.ImageField(upload_to='Core/PaymentMethod_Images/', null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    unique_id = models.CharField(max_length=13, null=True, blank=True)
    key = models.CharField(max_length=17, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return self.name


class Payments(models.Model):
    method = models.ForeignKey(PaymentMethods, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    phone = models.CharField(max_length=13)
    note = models.CharField(max_length=150)
    payment_id = models.BigIntegerField(default=100000000)
    transaction_id = models.BigIntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiation_user')
    cleared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='clearance_user')

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = "Payments"

    def __str__(self):
        return str(f'Payment Initiation of {self.amount}')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Handle payment ID increment for new records
            if self._state.adding:
                last_payment = Payments.objects.order_by('-payment_id').first()
                self.payment_id = last_payment.payment_id + 1 if last_payment else 100000000

            # Prevent task re-enqueueing if already being processed
            if not self.is_processed:
                self.is_processed = True  # Mark as processing before saving
                super().save(*args, **kwargs)  # Save the initial record
                from .tasks import process_and_update_payment
                # process_and_update_payment.delay(self.id)  # Enqueue Celery task
                process_and_update_payment.apply_async(
                    args=[self.id],  # Task arguments
                    #queue='payments',  # Optional: specify the queue
                    countdown=1  # Optional: delay execution by 5 seconds
                )
            else:
                super().save(*args, **kwargs)  # Save without triggering the task


class Refunds(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name=_('refund_user'))
    order_number = models.PositiveIntegerField(null=True, blank=True)
    ledger = models.ForeignKey(Ledger, on_delete=models.RESTRICT, null=True, blank=True, related_name='refund_ledger')
    phone = PhoneNumberField(null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    reason = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = "Refunds"

    def save(self, *args, **kwargs):
        # If phone number is missing, notify user about incomplete refund
        if self.phone is None:
            subject = f'Incomplete Refund for Ride {self.order_number}'
            message = (
                f"Dear Zyra user,\n\n"
                f"We attempted to process a refund of UGX {self.amount} for your ride (Order #{self.order_number}), "
                f"but could not complete it due to missing or incomplete profile details (such as your phone number).\n\n"
                f"Please update your profile with the necessary information to enable us to process your refund. "
                f"For assistance, contact Zyra support at support@zyra.app or call our helpline.\n\n"
                f"Thank you for riding with Zyra!\n\n"
                f"The Zyra Team"
            )
            if self.user and self.user.email:
                send_email_task.delay(self.user.email, subject, message)

        # If refund is successful, create a ledger entry and notify user
        if self.is_successful:
            create_ledger = Ledger.objects.create(
                user_to=self.user,
                amount=self.amount,
                is_valid=True,
                is_active=True,
                is_debit=True,
                notes=f'Client refund for ride (Order #{self.order_number}) due to: {self.reason}'
            )
            create_ledger.save()
            self.ledger = create_ledger
            subject = f'Refund for Ride {self.order_number} Processed'
            message = (
                f"Dear Zyra user,\n\n"
                f"A refund of UGX {self.amount} for your ride (Order #{self.order_number}) has been processed to your phone number {self.phone}.\n"
                f"Refund Reason: {self.reason}\n\n"
                f"If you have any questions or did not receive your refund, please contact Zyra support at support@zyra.app within 5 days.\n\n"
                f"Thank you for choosing Zyra.\n\n"
                f"The Zyra Team"
            )
            if self.user and self.user.email:
                send_email_task.delay(self.user.email, subject, message)

        super(Refunds, self).save(*args, **kwargs)

class MainWallet(models.Model):
    amount = models.DecimalField(max_digits=13, decimal_places=3)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Main Wallet as of {self.updated}'


class UserWallet(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_wallet')
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    points = models.DecimalField(max_digits=7, decimal_places=2)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}'s Wallet"


class Tip(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.SET_NULL, null=True, related_name='tip_sender')
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, related_name='tip_receiver')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    narrative = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_held = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client}'s tip to {self.driver}"


class Receipt(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ])

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['transaction_id'])
        ]

class Fare(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    cost_per_distance = models.DecimalField(max_digits=9, decimal_places=2)
    cost_per_time = models.DecimalField(max_digits=9, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)



Route.add_to_class("fare", models.ForeignKey(Fare, on_delete=models.SET_NULL, null=True, blank=True))
