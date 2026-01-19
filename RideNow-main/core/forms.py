from django import forms
from django.db import transaction
from django.utils.text import slugify
from django.forms.utils import ErrorList
from django.core.validators import MaxValueValidator, MinValueValidator,RegexValidator
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField

from .models import Contact, FAQ, NewsLetter, SystemUtility, SMS_Broadcast, User_Inquiry

class PhoneVerificationForm(forms.Form):
    phone_number = PhoneNumberField(
        region='UG',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter phone number',
            'class': 'form-control'
        })
    )

class OTPVerificationForm(forms.Form):
    phone_number = PhoneNumberField(
        region='UG',
        widget=forms.HiddenInput()
    )
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message='OTP must contain only digits',
                code='invalid_otp'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'class': 'form-control'
        })
    )

# Update your SystemUtilityModelForm to handle SMS configurations
class SystemUtilityModelForm(forms.ModelForm):
    class Meta:
        model = SystemUtility
        fields = [
            'root_email', 'root_phone', 'user_support_email', 
            'user_support_phone', 'send_sms_alert',
            'use_twilio_sms', 'use_africas_taking_sms'
        ]

    def clean(self):
        cleaned_data = super().clean()
        if SystemUtility.objects.exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Only one SystemUtility instance can exist!")
        
        use_twilio = cleaned_data.get('use_twilio_sms')
        use_africa = cleaned_data.get('use_africas_taking_sms')
        
        if not (use_twilio or use_africa):
            raise forms.ValidationError("At least one SMS service must be enabled")
        
        return cleaned_data
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('email', 'subject', 'message')


class UserInquiryForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'name':'Inquiry', 'rows':3, 'cols':5, 'placeholder': 'Describe to us the problem'}), label='Write your inquiry')
    class Meta:
        model = User_Inquiry
        fields = ('subject', 'message')
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Tell us what the problem is'}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ('question',)
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Ask your Question'}),
        }


class SystemUtilityModelForm(forms.ModelForm):
    def clean(self):
        if SystemUtility.objects.count() >= 1:
            self._errors.setdefault('__all__', ErrorList()).append("You can only create one Utility object!")
        return self.cleaned_data
    

class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetter
        fields = ( 'receivers', 'subject', 'message')


class BroadcastForm(forms.ModelForm):
    class Meta:
        model = SMS_Broadcast
        fields = ( 'receivers', 'message')

