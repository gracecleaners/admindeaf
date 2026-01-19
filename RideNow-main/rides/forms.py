from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Vehicle, VehicleType, VehiclePhoto, VehicleDocument,
    Ride, Rating, FeedBack, RideRequest
)


class RideRequestForm(forms.ModelForm):
    """Form for clients to request a ride"""
    
    class Meta:
        model = RideRequest
        fields = ['start_location', 'end_location', 'vehicle']
        widgets = {
            'start_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup location',
                'required': True
            }),
            'end_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination',
                'required': True
            }),
            'vehicle': forms.Select(attrs={
                'class': 'form-control',
                'required': False
            })
        }
        labels = {
            'start_location': 'Pickup Location',
            'end_location': 'Destination',
            'vehicle': 'Preferred Vehicle Type (Optional)'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Make vehicle optional
        self.fields['vehicle'].required = False
        self.fields['vehicle'].empty_label = "Any available vehicle"

    def clean(self):
        cleaned_data = super().clean()
        start_location = cleaned_data.get('start_location')
        end_location = cleaned_data.get('end_location')

        if start_location == end_location:
            raise ValidationError("Pickup location and destination cannot be the same.")

        return cleaned_data


class VehicleForm(forms.ModelForm):
    """Form for registering/updating vehicles"""
    
    class Meta:
        model = Vehicle
        fields = [
            'type', 'name', 'registration_number', 'description',
            'is_air_conditioned', 'is_insured', 'age'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Name'}),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., ABC123XY'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the vehicle'
            }),
            'is_air_conditioned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_insured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'age': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2020'})
        }

    def clean_registration_number(self):
        registration_number = self.cleaned_data.get('registration_number')
        # Check if registration number already exists (excluding current instance)
        qs = Vehicle.objects.filter(registration_number=registration_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A vehicle with this registration number already exists.")
        return registration_number


class VehiclePhotoForm(forms.ModelForm):
    """Form for uploading vehicle photos"""
    
    class Meta:
        model = VehiclePhoto
        fields = ['photo']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5MB )")
            # Check file extension
            if not photo.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError("Only image files are allowed (jpg, jpeg, png, gif)")
        return photo


class VehicleDocumentForm(forms.ModelForm):
    """Form for uploading vehicle documents"""
    
    class Meta:
        model = VehicleDocument
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File too large ( > 10MB )")
        return file


class RatingForm(forms.ModelForm):
    """Form for rating a completed ride"""
    
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rate your ride'
    )
    
    class Meta:
        model = Rating
        fields = ['rating']

    def __init__(self, *args, **kwargs):
        self.ride = kwargs.pop('ride', None)
        self.client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)

    def clean_rating(self):
        rating = int(self.cleaned_data.get('rating'))
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
        return rating

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.ride:
            instance.ride = self.ride
        if self.client:
            instance.client = self.client
        if commit:
            instance.save()
        return instance


class FeedBackForm(forms.ModelForm):
    """Form for providing feedback on a ride"""
    
    class Meta:
        model = FeedBack
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with us...',
                'required': True
            })
        }
        labels = {
            'message': 'Your Feedback'
        }

    def __init__(self, *args, **kwargs):
        self.ride = kwargs.pop('ride', None)
        self.client = kwargs.pop('client', None)
        self.rating = kwargs.pop('rating', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.ride:
            instance.ride = self.ride
        if self.client:
            instance.client = self.client
        if self.rating:
            instance.rating = self.rating
        if commit:
            instance.save()
        return instance


class RideRequestAcceptForm(forms.Form):
    """Form for drivers to accept ride requests"""
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select your vehicle',
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.driver = kwargs.pop('driver', None)
        super().__init__(*args, **kwargs)
        
        # Filter vehicles to show only those owned by the driver
        if self.driver:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(
                driverprofile=self.driver
            )


class RideSearchForm(forms.Form):
    """Form for searching rides"""
    start_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by pickup location'
        })
    )
    end_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by destination'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Statuses'),
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class VehicleTypeForm(forms.ModelForm):
    """Form for creating/editing vehicle types"""
    
    class Meta:
        model = VehicleType
        fields = ['name', 'description', 'engine_type', 'vehicle_capacity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sedan, SUV, Motorcycle'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'engine_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_capacity': forms.Select(attrs={'class': 'form-control'})
        }

