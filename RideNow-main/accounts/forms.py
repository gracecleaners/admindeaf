from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm, UserCreationForm
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField
from django.db import transaction
from django.core.exceptions import ValidationError
import uuid
from .models import User, ClientProfile, DriverProfile, UserPreferences, UserSecuritySettings

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating basic profile information"""
    first_name = forms.CharField(
        max_length=75,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=75,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Last Name'
        })
    )
    other_name = forms.CharField(
        max_length=75,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Other Name (Optional)'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Email Address'
        })
    )
    phone = PhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '+256 700 000 000'
        })
    )
    country = CountryField().formfield(
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'type': 'date'
        })
    )
    city = forms.CharField(
        max_length=75,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'City'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        })
    )
    interests = forms.CharField(
        max_length=175,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'e.g Sports, Travel, Vlogging, Engineering, Medicine'
        })
    )

    class Meta:
        model = ClientProfile
        fields = ['first_name', 'last_name', 'other_name', 'email', 'phone', 'country', 'gender', 'date_of_birth', 'city', 'bio', 'interests']


# General User Change Form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username','email')

class CreateUserForm(UserCreationForm):
	password1 = forms.CharField(widget=forms.PasswordInput(), label='Create a Password', help_text='Create a minimum 8 characters of letters, symbols and numbers')
	password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirm your password', help_text='Enter password as before')


class UserSignUpForm(CreateUserForm):
	# username = forms.CharField(max_length=15, widget=forms.TextInput(
	# 	attrs={
	# 		'placeholder': 'e.g Sonia'
	# 	}),   help_text='Must be unique.', label='Create a username for your account')
	class Meta(UserCreationForm.Meta):
		model = User
		fields = ('username', 'email',)
		widgets = {
			'email': forms.EmailInput(attrs={'placeholder': 'e.g example@shukrani.shop'}),
			# 'password1': forms.PasswordInput(attrs={'placeholder': '**************'}),
		}

	@transaction.atomic
	def save(self):
		user = super().save(commit=False)
		user.is_active = False
		user.is_staff = False
		user.referral_code = uuid.uuid4()
		user.save()
		profile = ClientProfile.objects.create(user=user)
		profile.username = self.cleaned_data.get('username')
		profile.email = self.cleaned_data.get('email')
		profile.save()
		return user

	# Validating the username to ensure it's unique
	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise ValidationError('Username already taken. Please choose another one.')
		return username
	
	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise ValidationError('Email not available')
		return email


class DriverProfileUpdateForm(ProfileUpdateForm):
    """Form for updating driver-specific profile information"""
    vehicle_registration = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Vehicle Registration Number'
        })
    )
    drivers_license_no = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Driver\'s License Number'
        })
    )
 



class PhotoUpdateForm(forms.ModelForm):
    """Form for updating profile and cover photos"""
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        })
    )
    cover_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = ClientProfile
        fields = ['photo', 'cover_photo']

class DriverPhotoUpdateForm(forms.ModelForm):
    """Form for updating driver profile and cover photos"""
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        })
    )
    cover_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = DriverProfile
        fields = ['photo', 'cover_photo']

class PreferencesForm(forms.ModelForm):
    """Form for user preferences and settings"""
    class Meta:
        model = UserPreferences
        fields = [
            'email_notifications', 'sms_notifications', 'push_notifications', 'marketing_emails',
            'profile_visibility', 'language', 'timezone', 'preferred_payment_method',
            'auto_accept_rides', 'max_ride_distance', 'preferred_ride_types',
            'preferred_driver_rating', 'preferred_vehicle_type'
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'push_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'marketing_emails': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'profile_visibility': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'timezone': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'preferred_payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'auto_accept_rides': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'max_ride_distance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1',
                'max': '200'
            }),
            'preferred_ride_types': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g. Standard, Premium, Shared'
            }),
            'preferred_driver_rating': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1.0',
                'max': '5.0',
                'step': '0.1'
            }),
            'preferred_vehicle_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }

class SecurityForm(forms.ModelForm):
    """Form for security settings"""
    class Meta:
        model = UserSecuritySettings
        fields = [
            'two_factor_enabled', 'login_alerts', 'session_timeout', 'max_concurrent_sessions',
            'data_sharing_consent', 'analytics_consent', 'location_tracking', 'api_access_enabled'
        ]
        widgets = {
            'two_factor_enabled': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'login_alerts': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'session_timeout': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '15',
                'max': '1440'
            }),
            'max_concurrent_sessions': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1',
                'max': '10'
            }),
            'data_sharing_consent': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'analytics_consent': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'location_tracking': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'api_access_enabled': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }

class AccountDeletionForm(forms.Form):
    """Form for account deletion confirmation"""
    confirm_deletion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500'
        })
    )
    reason = forms.ChoiceField(
        choices=[
            ('', 'Select a reason (optional)'),
            ('privacy', 'Privacy concerns'),
            ('not_using', 'Not using the service'),
            ('found_alternative', 'Found a better alternative'),
            ('technical_issues', 'Technical issues'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent'
        })
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent',
            'rows': 3,
            'placeholder': 'Please let us know how we can improve...'
        })
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Current Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Confirm New Password'
        })


class OTPSendForm(forms.Form):
    """Form for sending OTP"""
    email_or_phone = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Email or Phone Number'
        })
    )


class OTPVerifyForm(forms.Form):
    """Form for verifying OTP"""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6'
        })
    )