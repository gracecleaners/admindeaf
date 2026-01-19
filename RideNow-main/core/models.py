from collections.abc import Iterable
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from accounts.models import User
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField


from datetime import timedelta


class SystemUtility(models.Model):
   root_email = models.EmailField(help_text=_('Management Email for the System'))
   root_phone = PhoneNumberField(
       help_text=_('Management Phone Number for the system'),
       region='KE'  # Set region for validation
   )
   user_support_email = models.EmailField(help_text=_('User Support Email'))
   user_support_phone = PhoneNumberField(
       help_text=_('User Support Phone'),  # Fixed help text
       region='KE'
   )
   transaction_phone = PhoneNumberField(
       blank=True, 
       null=True,
       help_text=_('Transaction Phone'),
       region='KE'
   )
   sales_commission = models.PositiveIntegerField(
       help_text='Commissions charged for Items sold', 
       default=7
   )
   info = RichTextField(blank=True, null=True)
   privacy_policy = RichTextField(blank=True, null=True)
   terms_of_use = RichTextField(blank=True, null=True)
   address = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Main Address'))
   address2 = models.CharField(max_length=250, null=True, blank=True)
   address3 = models.CharField(max_length=250, null=True, blank=True)
   meta_keywords = models.CharField(max_length=355, null=True, blank=True)
   meta_description = models.TextField(null=True, blank=True)
   send_emails_alert = models.BooleanField(default=True)
   use_gmail_smtp = models.BooleanField(default=True)
   use_zoho_mail_smtp = models.BooleanField(default=False)
   send_sms_alert = models.BooleanField(default=True)
   use_twilio_sms = models.BooleanField(default=False)
   use_africas_taking_sms = models.BooleanField(default=True)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)

   _metadata = {
       'title': 'title',
       'keywords': 'meta_keywords', 
       'description': 'meta_description',
   }

   class Meta:
       verbose_name = _('SystemUtility')
       verbose_name_plural = _('SystemUtility')
       db_table = 'system_utility'
       indexes = [
           models.Index(fields=['created']),
           models.Index(fields=['updated'])
       ]

   def clean(self):
       if not (self.use_twilio_sms or self.use_africas_taking_sms):
           raise ValidationError(_('At least one SMS service must be enabled'))
       if not (self.use_gmail_smtp or self.use_zoho_mail_smtp):
           raise ValidationError(_('At least one email service must be enabled'))

   def __str__(self):
       return f'RideNow Management Utility as of {self.updated}'

class PhoneNumber(models.Model):
	utility = models.ForeignKey(SystemUtility, on_delete=models.SET_NULL, null=True, blank=True, related_name='utility_phone')
	name = models.CharField(verbose_name=_('Phone Number Name'), max_length=75)
	number = PhoneNumberField()

	def __str__(self):
		return str(self.name)


class SystemEmail(models.Model):
	utility = models.ForeignKey(SystemUtility, on_delete=models.SET_NULL, null=True, blank=True, related_name='utility_email')
	name = models.CharField(verbose_name=_('Email Name'), max_length=75)
	email = models.EmailField()

	def __str__(self):
		return str(self.name)


class FAQ(models.Model):
	question = models.CharField(max_length=250)
	answer = RichTextField()
	is_answered = models.BooleanField(default=False)
	is_archived = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _('FAQ')

	def __str__(self):
		return str(self.question)

	def save(self, *args, **kwargs):
		if self.answer == '':
			self.is_answered = False
		else:
			self.is_answered = True 
		super(FAQ, self).save(*args, **kwargs)


class Contact(models.Model):
	email = models.EmailField(verbose_name=_('Your Email'))
	subject = models.CharField(max_length=150)
	message = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


class User_Inquiry(Contact):
	is_answered = models.BooleanField(default=False) 
	post_inquiry = models.BooleanField(default=False)
	answer = RichTextField(null=True, blank=True)
	user = models.ForeignKey(User, related_name='inquiry_user', on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		verbose_name = 'User Inquiry'
		verbose_name_plural = 'User Inquiries'

	def save(self, *args, **kwargs):
		if self.answer is not None:
			self.is_answered = True
		return super(User_Inquiry, self).save(*args, **kwargs)

	def __str__(self):
		return str(self.subject)


class Action(models.Model):
	user = models.ForeignKey(User, related_name='actions', db_index=True, on_delete=models.CASCADE, blank=True, null=True,)
	verb = models.CharField(max_length=255)
	target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj', on_delete=models.CASCADE)
	target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
	target = GenericForeignKey('target_ct', 'target_id')
	timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ('-timestamp',)

	def __str__(self):
		return '{0} :: {1}, {2}'.format(
			self.target_id, self.user, self.timestamp)


class EmailSubscription(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='email_subscription')
	email = models.EmailField()
	is_active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Email Subscription'

	def __str__(self):
		return self.email


class NewsLetter(models.Model):
	subject = models.CharField(max_length=355)
	message = RichTextField(verbose_name=_('News Letter Content'))
	images = models.ImageField(blank=True, null=True, upload_to='Images/news_letters')
	receivers = models.CharField(max_length=1000)
	is_active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


	class Meta:
		verbose_name = 'News Letter'
		verbose_name_plural = 'News Letters'

	def __str__(self):
		return self.subject


class SEOMetaData(models.Model):
	name = models.CharField(max_length=20)
	abstract = models.TextField()
	image = models.ImageField()

	_metadata = {
		'title': 'name',
		'description': 'abstract',
		'image': 'get_meta_image',
	}

	def get_meta_image(self):
		if self.image:
			return self.image.url


class SMS_Subscription(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_subscription')
	phone = PhoneNumberField()
	is_active = models.BooleanField(default=True)
	created = models.DateField(auto_now_add=True)
	updated = models.DateField(auto_now=True)

	def __str__(self):
		return f'{self.phone}'
	
	class Meta:
		verbose_name = 'SMS Subscription'
		verbose_name_plural = 'SMS Subscriptions'


class SMS_Broadcast(models.Model):
	receivers = models.CharField(max_length=1000, null=True, blank=True)
	subject = models.CharField(max_length=150)
	message = models.TextField()
	is_active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'SMS Broadcast'
		verbose_name_plural = 'SMS Broadcasts'

	def __str__(self):
		return self.subject
	
	def save(self, *args, **kwargs):
		self.receivers = ','.join([f'{active_subscription.phone}' for active_subscription in SMS_Subscription.objects.filter(is_active=True)])
		super(SMS_Broadcast, self).save(*args, **kwargs)


class Update(models.Model):
	subject = models.CharField(max_length=150)
	description = RichTextField()
	image_illustration = models.ImageField(upload_to='Updates/Illustrations')
	due_date = models.DateTimeField()
	is_active = models.BooleanField(default=True)
	is_archived = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.subject)


class File(models.Model):
	CATEGORY_CHOICES = (
        ('App', 'Application'),
        ('Document', 'Document'),
		('Audio', 'Audio'),
		('Video', 'Video'),
    )
	name = models.CharField(max_length=35, verbose_name='File Name')
	file = models.FileField(upload_to='core/files/%Y/%M/%d')
	thumbnail = models.ImageField(upload_to='core/files/thumbnails', verbose_name='File thumbnail', null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	download_count = models.PositiveBigIntegerField(default=0)
	category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='App')
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class ErrorLogs(models.Model):
	error_narration = models.TextField()
	traceback = models.TextField(null=True, blank=True)
	type = models.CharField(max_length=255, null=True, blank=True)
	code = models.CharField(max_length=255, null=True, blank=True)
	file = models.CharField(max_length=255, null=True, blank=True)
	line = models.IntegerField(null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'ErrorLog'
		verbose_name_plural = 'ErrorLogs'


class Notification(models.Model):
    message = models.CharField(max_length=200)
    
    def __str__(self):
        return self.message
	
class OTP(models.Model):
    phone_number = PhoneNumberField(
        verbose_name="Phone Number",
        help_text="Phone number in international format"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email address",
        null=True,
        blank=True
    )
    otp = models.CharField(
        max_length=6,
        verbose_name="One-Time Password"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if this OTP has been verified"
    )
    attempt_count = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of verification attempts"
    )
    max_attempts = models.PositiveSmallIntegerField(
        default=3,
        help_text="Maximum number of verification attempts allowed"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the OTP was created"
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when the OTP expires"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this OTP is still active"
    )

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'otp']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"OTP for {self.phone_number} - {'Verified' if self.is_verified else 'Unverified'}"

    def save(self, *args, **kwargs):
        # Set expiration time if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the OTP has expired"""
        return timezone.now() > self.expires_at

    @property
    def can_attempt_verification(self):
        """Check if verification can be attempted"""
        return (
            self.is_active and
            not self.is_verified and
            not self.is_expired and
            self.attempt_count < self.max_attempts
        )

    def increment_attempt(self):
        """Increment the attempt counter"""
        self.attempt_count += 1
        if self.attempt_count >= self.max_attempts:
            self.is_active = False
        self.save()

    def verify(self, otp_input):
        """
        Verify the OTP input
        Returns True if verification successful, False otherwise
        """
        if not self.can_attempt_verification:
            return False

        self.increment_attempt()
        
        if str(self.otp) == str(otp_input):
            self.is_verified = True
            self.is_active = False
            self.save()
            return True
            
        return False

    @classmethod
    def generate_otp(cls, phone_number):
        """
        Generate a new OTP for the given phone number
        Deactivates any existing active OTPs for this phone number
        """
        # Deactivate existing active OTPs
        cls.objects.filter(
            phone_number=phone_number,
            is_active=True
        ).update(is_active=False)

        # Generate new OTP
        from django.utils.crypto import get_random_string
        otp = get_random_string(6, allowed_chars='0123456789')
        
        # Create new OTP instance
        return cls.objects.create(
            phone_number=phone_number,
            otp=otp
        )