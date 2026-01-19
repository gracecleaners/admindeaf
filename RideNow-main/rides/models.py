from django.utils import timezone
from django.contrib.gis.db import models

from ckeditor.fields import RichTextField

from accounts.models import User, ClientProfile, DriverProfile


# Create your models here.
class VehicleType(models.Model):
    ENGINE_CAPACITIES = (
        ('100cc', '100cc to 150cc'),
        ('151cc', '151cc to 250cc'),
        ('251cc', '251cc to 500cc'),
        ('501cc', '501cc to 1000cc'),
        ('1001cc', '1001cc to 1500cc'),
        ('1501cc', '1501cc to 2000cc'),
        ('2001cc', '2001cc to 2500cc'),
        ('2501cc', '2501cc to 3000cc'),
        ('3001cc', '3001cc to 3500cc'),
        ('3501cc', '3501cc to 4000cc'),
        ('4001cc', '4001cc to 4500cc'),
        ('4501cc', '4501cc to 5000cc'),
        ('5001cc', '5001cc to 6000cc'),
        ('6001cc', '6001cc and above'),
    )

    VEHICLE_CAPACITIES = (
        ('1 seater', '1 seater'),
        ('2 seater', '2 seater'),
        ('3 seater', '3 seater'),
        ('4 seater', '4 seater'),
        ('5 seater', '5 seater'),
        ('6 seater', '6 seater'),
        ('7 seater', '7 seater'),
        ('8 seater', '8 seater'),
        ('9 seater', '9 seater'),
        ('10 seater', '10 seater'),
        ('12 seater', '12 seater'),
        ('15 seater', '15 seater'),
        ('18 seater', '18 seater'),
        ('20 seater', '20 seater'),
        ('22 seater', '22 seater'),
        ('24 seater', '24 seater'),
        ('26 seater', '26 seater'),
        ('28 seater', '28 seater'),
        ('30 seater', '30 seater'),
        ('32 seater', '32 seater'),
        ('34 seater', '34 seater'),
        ('36 seater', '36 seater'),
        ('38 seater', '38 seater'),
        ('40 seater', '40 seater'),
        ('42 seater', '42 seater'),
        ('44 seater', '44 seater'),
        ('46 seater', '46 seater'),
        ('48 seater', '48 seater'),
        ('50 seater', '50 seater'),
        ('52 seater', '52 seater'),
        ('54 seater', '54 seater'),
        ('56 seater', '56 seater'),
        ('58 seater', '58 seater'),
        ('60 seater', '60 seater'),
    )
    VEHICLE_TYPES = (
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('mini-bus', 'Mini-Bus'),
        ('lorry', 'Lorry'),
        ('trailer', 'Trailer'),
        ('pickup', 'Pickup'),
        ('SUV', 'SUV'),
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('cabriolet', 'Cabriolet'),
        ('roadster', 'Roadster'),
        ('targa', 'Targa'),
        ('hardtop', 'Hardtop'),
        ('rikshaw', 'Rikshaw'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=225, choices=VEHICLE_TYPES, null=True, blank=True)
    description = RichTextField()
    engine_type = models.CharField(max_length=225, choices=ENGINE_CAPACITIES, null=True, blank=True)
    vehicle_capacity = models.CharField(max_length=225, choices=VEHICLE_CAPACITIES, null=True, blank=True)
    
    # Pricing fields
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00, help_text="Base price in UGX")
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, help_text="Price per kilometer in UGX")

    def __str__(self):
        return f"{self.name}"


class Vehicle(models.Model):
    type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=225)
    description = RichTextField()
    is_air_conditioned = models.BooleanField(default=False)
    is_insured = models.BooleanField(default=False)
    age = models.CharField(max_length=50)
    manufacturing_year = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.registration_number}"

    def get_age(self):
        """
        Returns the age of the vehicle in years based on the manufacturing year.
        If manufacturing_year is not set, returns None.
        """
        if self.manufacturing_year:
            return timezone.now().year - self.manufacturing_year.year
        return None

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically update the vehicle's age
        based on the manufacturing year before saving.
        """
        age = self.get_age()
        self.age = str(age) if age is not None else ""
        super().save(*args, **kwargs)


class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="vehicle_photos/%Y/%M/%d")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.name} - {self.photo.name}"


class VehicleDocument(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    file = models.FileField(upload_to="vehicle_files/%Y/%M/%d")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.name} - {self.file.name}"


class Route(models.Model):
    pickup_location = models.PointField(srid=4326)
    destination = models.PointField(srid=4326)
    eta = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pickup_location} - {self.destination}"


class Ride(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(ClientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver} - {self.client} - {self.vehicle}"

class Rating(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveIntegerField(default=0, verbose_name=("Star Ratings"), help_text="Give star rating")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return str(f"{self.ride.driver} - {self.ride.client} - {self.rating}")

class FeedBack(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True, blank=True)
    message = RichTextField()
    rating = models.OneToOneField(Rating, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"User feedback for ride {self.ride.id}")
    

DriverProfile.add_to_class("vehicle", models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True))


class DriverScore(models.Model):
    """Track driver performance scores for better matching"""
    driver = models.OneToOneField(DriverProfile, on_delete=models.CASCADE, related_name='score')
    
    # Performance metrics
    acceptance_rate = models.FloatField(default=100.0, help_text="Percentage of ride requests accepted")
    response_time_avg = models.FloatField(default=0.0, help_text="Average response time in seconds")
    cancellation_rate = models.FloatField(default=0.0, help_text="Percentage of rides cancelled by driver")
    completion_rate = models.FloatField(default=100.0, help_text="Percentage of rides completed")
    
    # Scoring factors
    reliability_score = models.FloatField(default=100.0, help_text="Overall reliability score (0-100)")
    availability_score = models.FloatField(default=100.0, help_text="Availability score based on online time")
    
    # Statistics
    total_requests = models.PositiveIntegerField(default=0, help_text="Total ride requests received")
    accepted_requests = models.PositiveIntegerField(default=0, help_text="Total requests accepted")
    declined_requests = models.PositiveIntegerField(default=0, help_text="Total requests declined")
    timeout_requests = models.PositiveIntegerField(default=0, help_text="Total requests that timed out")
    cancelled_rides = models.PositiveIntegerField(default=0, help_text="Total rides cancelled by driver")
    completed_rides = models.PositiveIntegerField(default=0, help_text="Total rides completed")
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Driver Score'
        verbose_name_plural = 'Driver Scores'
    
    def __str__(self):
        return f"{self.driver.user.get_user_names} - Score: {self.reliability_score}"
    
    def update_scores(self):
        """Recalculate all scores based on current statistics"""
        if self.total_requests > 0:
            self.acceptance_rate = (self.accepted_requests / self.total_requests) * 100
            self.cancellation_rate = (self.cancelled_rides / max(self.accepted_requests, 1)) * 100
        
        if self.accepted_requests > 0:
            self.completion_rate = (self.completed_rides / self.accepted_requests) * 100
        
        # Calculate reliability score (0-100)
        # Factors: acceptance rate (40%), completion rate (40%), response time (20%)
        acceptance_factor = min(self.acceptance_rate / 100, 1.0)
        completion_factor = min(self.completion_rate / 100, 1.0)
        
        # Response time factor (faster is better, max 2 minutes = 120 seconds)
        response_factor = max(0, 1.0 - (self.response_time_avg / 120))
        
        self.reliability_score = (
            acceptance_factor * 40 +
            completion_factor * 40 +
            response_factor * 20
        )
        
        self.save()


class DriverLocationHistory(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    location = models.PointField(srid=4326, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    on_active_ride = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver.user.get_user_names} @ {self.latitude}, {self.longitude} {self.timestamp}"

    def save(self, *args, **kwargs):
        """
        Overrides the save method
        """
        super().save(*args, **kwargs)



class DriverLocation(models.Model):
    """Track driver's current location for matching with clients"""
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='locations')
    location = models.PointField(srid=4326)  # Longitude, Latitude
    address = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.BooleanField(default=True)
    on_active_ride = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)  # Available for new rides
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Driver Location'
        verbose_name_plural = 'Driver Locations'
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.driver.user.get_user_names} - {self.address or 'Unknown Location'}"
    
    @property
    def latitude(self):
        return self.location.y if self.location else None
    
    @property
    def longitude(self):
        return self.location.x if self.location else None

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically create a driver location history
        """
        super().save(*args, **kwargs)
        if not DriverLocationHistory.objects.filter(driver=self.driver, location=self.location).exists():
            DriverLocationHistory.objects.create(
                driver=self.driver,
                location=self.location,
                address=self.address,
                on_active_ride=self.on_active_ride
            )


# RideRequest Model
class RideRequest(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="ride_requests", null=True, blank=True)
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="ride_requests")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="ride_requests")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="ride_requests")
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    requested_at = models.DateTimeField(default=timezone.now)  # Time when the request was made
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')
    ride = models.ForeignKey('Ride', on_delete=models.SET_NULL, null=True, blank=True, related_name="ride_requests")  # Link to the actual ride once assigned
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Ride cost in UGX")
    
    # Enhanced fields for matching system
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this request expires if no driver accepts")
    matching_started_at = models.DateTimeField(null=True, blank=True, help_text="When driver matching started")
    driver_confirmed_at = models.DateTimeField(null=True, blank=True, help_text="When driver confirmed the ride")
    pickup_eta = models.DateTimeField(null=True, blank=True, help_text="Estimated pickup time")
    
    # Sequential matching fields
    potential_drivers = models.JSONField(default=list, blank=True, help_text="List of driver IDs to contact sequentially")
    current_driver_index = models.IntegerField(default=0, help_text="Index of current driver being contacted")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RideRequest {self.id} by {self.client.user.get_user_names}"

    # Add a method to update the status
    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

class RideMatching(models.Model):
    """Track ride matching attempts and results"""
    ride_request = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='matching_attempts')
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    distance_km = models.FloatField(help_text="Distance in kilometers")
    estimated_eta_minutes = models.IntegerField(help_text="Estimated arrival time in minutes")
    matching_score = models.FloatField(help_text="Matching score based on distance, rating, etc.")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('timeout', 'Timeout'),
    ], default='pending')
    
    # Enhanced fields for timeout and scoring
    expires_at = models.DateTimeField(default=timezone.now, help_text="When this match expires if not accepted")
    responded_at = models.DateTimeField(null=True, blank=True, help_text="When driver responded")
    response_time_seconds = models.IntegerField(null=True, blank=True, help_text="How long driver took to respond")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ride Matching'
        verbose_name_plural = 'Ride Matchings'
        ordering = ['-matching_score', 'distance_km']
        unique_together = ['ride_request', 'driver']
    
    def __str__(self):
        return f"Match: {self.ride_request.id} -> {self.driver.user.get_user_names} (Score: {self.matching_score})"
    
    def is_expired(self):
        """Check if this match has expired"""
        if self.status in ['accepted', 'declined']:
            return False
        return timezone.now() > self.expires_at
    
    def accept(self):
        """Accept this match"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        if self.created:
            self.response_time_seconds = int((self.responded_at - self.created).total_seconds())
        self.save()
    
    def decline(self):
        """Decline this match"""
        self.status = 'declined'
        self.responded_at = timezone.now()
        if self.created:
            self.response_time_seconds = int((self.responded_at - self.created).total_seconds())
        self.save()